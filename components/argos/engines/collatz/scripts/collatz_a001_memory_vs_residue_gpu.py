#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence

import numpy as np

try:
    import pyopencl as cl
except ImportError as exc:
    raise SystemExit(
        "pyopencl absent. Installe-le avec: sudo apt install python3-pyopencl"
    ) from exc

ALPHA = 0.5

KERNEL = r"""
__kernel void collatz_k_stream(
    __global const ulong *starts,
    __global uchar *ks,
    __global ushort *residues,
    __global ushort *lengths,
    const uint step_limit,
    const uint residue_mask
) {
    const uint gid = get_global_id(0);
    ulong n = starts[gid];

    if (n == 0UL) {
        lengths[gid] = 0;
        return;
    }

    while ((n & 1UL) == 0UL) {
        n >>= 1;
    }

    uint len = 0;
    const ulong max_before_mul = (0xffffffffffffffffUL - 1UL) / 3UL;

    for (uint step = 0; step < step_limit; ++step) {
        if (n == 1UL) break;
        if (n > max_before_mul) break;

        ulong x = 3UL * n + 1UL;
        uchar k = (uchar)ctz(x);
        n = x >> k;

        const size_t idx = ((size_t)gid * step_limit) + step;
        ks[idx] = k;
        residues[idx] = (ushort)(n & residue_mask);
        len++;
    }

    lengths[gid] = (ushort)min(len, (uint)65535);
}
"""


def detect_start_column(fieldnames: Sequence[str]) -> str:
    by_lower = {name.lower(): name for name in fieldnames}
    for candidate in ("n", "start", "start_n", "input", "value", "seed"):
        if candidate in by_lower:
            return by_lower[candidate]
    raise RuntimeError("Colonne de départ introuvable: " + ", ".join(fieldnames))


def load_starts(path: Path, max_rows: int | None) -> np.ndarray:
    values: list[int] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError("CSV sans en-tête")
        column = detect_start_column(reader.fieldnames)
        for row_index, row in enumerate(reader):
            if max_rows is not None and row_index >= max_rows:
                break
            raw = (row.get(column) or "").strip()
            if not raw:
                continue
            n = int(raw)
            if 0 < n <= np.iinfo(np.uint64).max:
                values.append(n)
    if not values:
        raise RuntimeError("Aucun entier positif uint64 trouvé")
    return np.asarray(values, dtype=np.uint64)


def entropy_bits(counts: Counter[int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def weighted_entropy(table: dict[object, Counter[int]]) -> float:
    total = sum(sum(c.values()) for c in table.values())
    if total == 0:
        return 0.0
    return sum((sum(c.values()) / total) * entropy_bits(c) for c in table.values())


def is_test(trajectory_id: int, step: int, fraction: float) -> bool:
    digest = hashlib.sha256(f"{trajectory_id}:{step}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64 < fraction


def mean_test_nll_bits(
    train: dict[object, Counter[int]],
    global_counts: Counter[int],
    test_rows: list[tuple[object, int]],
) -> float:
    labels = sorted(global_counts)
    if not labels or not test_rows:
        return math.nan
    total = 0.0
    for key, target in test_rows:
        counts = train.get(key, global_counts)
        denom = sum(counts.values()) + ALPHA * len(labels)
        p = (counts.get(target, 0) + ALPHA) / denom
        total -= math.log2(p)
    return total / len(test_rows)


def pack_word(values: np.ndarray) -> int:
    # 6 bits par k; les valeurs >63 sont saturées pour garder une clé compacte.
    result = 0
    for value in values:
        result = (result << 6) | min(int(value), 63)
    return result


def choose_device() -> tuple[cl.Context, cl.CommandQueue, cl.Device]:
    devices = []
    for platform in cl.get_platforms():
        for device in platform.get_devices():
            devices.append(device)

    gpu_devices = [d for d in devices if d.type & cl.device_type.GPU]
    if not gpu_devices:
        raise RuntimeError("Aucun GPU OpenCL détecté")

    device = max(gpu_devices, key=lambda d: d.global_mem_size)
    context = cl.Context([device])
    queue = cl.CommandQueue(
        context,
        properties=cl.command_queue_properties.PROFILING_ENABLE,
    )
    return context, queue, device


def main() -> int:
    ap = argparse.ArgumentParser(
        description="CAMP-A001-0001 GPU OpenCL — mémoire contre résidu."
    )
    ap.add_argument("workspace_csv", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--word-length", type=int, default=6)
    ap.add_argument("--step-limit", type=int, default=1000)
    ap.add_argument("--max-memory-words", type=int, default=6)
    ap.add_argument("--max-residue-power", type=int, default=12)
    ap.add_argument("--max-rows", type=int)
    ap.add_argument("--test-fraction", type=float, default=0.25)
    ap.add_argument("--batch-size", type=int, default=32768)
    ap.add_argument(
        "--focused",
        action="store_true",
        help="Teste uniquement word, mod8, mod16 et mémoire 2..6.",
    )
    args = ap.parse_args()

    if args.step_limit > 65535:
        raise RuntimeError("--step-limit doit être <= 65535")
    if args.max_residue_power > 16:
        raise RuntimeError("--max-residue-power doit être <= 16")

    starts = load_starts(args.workspace_csv, args.max_rows)
    context, queue, device = choose_device()
    program = cl.Program(context, KERNEL).build()

    if args.focused:
        residue_powers = [3, 4]
    else:
        residue_powers = [1, 2, 3, 4, 5, 6, 8, 10, 12]
        residue_powers = [p for p in residue_powers if p <= args.max_residue_power]

    specs: list[tuple[str, str, int, int | None]] = [("word", "word", 1, None)]
    for p in residue_powers:
        specs.append((f"word_mod_2^{p}", "residue", 1, 1 << p))
    for depth in range(2, args.max_memory_words + 1):
        specs.append((f"memory_{depth}_words", "memory", depth, None))
        if not args.focused:
            for p in residue_powers:
                specs.append(
                    (f"memory_{depth}_words_mod_2^{p}", "both", depth, 1 << p)
                )

    train = {name: defaultdict(Counter) for name, _, _, _ in specs}
    tests: dict[str, list[tuple[object, int]]] = defaultdict(list)
    global_train: Counter[int] = Counter()
    word_counts: dict[int, Counter[int]] = defaultdict(Counter)

    mf = cl.mem_flags
    total_events = 0
    gpu_ns = 0
    wall_start = time.perf_counter()
    residue_mask = (1 << args.max_residue_power) - 1

    for batch_start in range(0, len(starts), args.batch_size):
        batch = np.ascontiguousarray(
            starts[batch_start : batch_start + args.batch_size]
        )
        count = len(batch)

        ks = np.empty((count, args.step_limit), dtype=np.uint8)
        residues = np.empty((count, args.step_limit), dtype=np.uint16)
        lengths = np.empty(count, dtype=np.uint16)

        starts_buf = cl.Buffer(
            context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=batch
        )
        ks_buf = cl.Buffer(context, mf.WRITE_ONLY, ks.nbytes)
        residues_buf = cl.Buffer(context, mf.WRITE_ONLY, residues.nbytes)
        lengths_buf = cl.Buffer(context, mf.WRITE_ONLY, lengths.nbytes)

        event = program.collatz_k_stream(
            queue,
            (count,),
            None,
            starts_buf,
            ks_buf,
            residues_buf,
            lengths_buf,
            np.uint32(args.step_limit),
            np.uint32(residue_mask),
        )
        event.wait()
        gpu_ns += event.profile.end - event.profile.start

        cl.enqueue_copy(queue, ks, ks_buf)
        cl.enqueue_copy(queue, residues, residues_buf)
        cl.enqueue_copy(queue, lengths, lengths_buf)
        queue.finish()

        for local_id in range(count):
            trajectory_id = batch_start + local_id
            length = int(lengths[local_id])
            if length <= args.word_length:
                continue

            row_ks = ks[local_id, :length]
            row_residues = residues[local_id, :length]
            words = [
                pack_word(row_ks[end - args.word_length + 1 : end + 1])
                for end in range(args.word_length - 1, length - 1)
            ]

            for index, word in enumerate(words):
                end = index + args.word_length - 1
                step = end
                k_next = int(row_ks[end + 1])
                n_residue = int(row_residues[end])
                total_events += 1
                word_counts[word][k_next] += 1

                test = is_test(trajectory_id, step, args.test_fraction)
                if not test:
                    global_train[k_next] += 1

                for name, mode, depth, modulus in specs:
                    if depth > index + 1:
                        continue
                    memory = tuple(words[index - depth + 1 : index + 1])

                    if mode == "word":
                        key: object = word
                    elif mode == "residue":
                        key = (word, n_residue % modulus)
                    elif mode == "memory":
                        key = memory
                    else:
                        key = (memory, n_residue % modulus)

                    if test:
                        tests[name].append((key, k_next))
                    else:
                        train[name][key][k_next] += 1

        done = batch_start + count
        print(
            f"\rGPU {done}/{len(starts)} starts "
            f"events={total_events}",
            end="",
            flush=True,
        )

    print()

    rows: list[dict] = []
    baseline_nll = math.nan
    for name, _, _, _ in specs:
        table = train[name]
        nll = mean_test_nll_bits(table, global_train, tests[name])
        if name == "word":
            baseline_nll = nll
        states = len(table)
        deterministic = sum(1 for c in table.values() if len(c) == 1)
        rows.append(
            {
                "model": name,
                "train_states": states,
                "test_events": len(tests[name]),
                "conditional_entropy_bits_train": weighted_entropy(table),
                "mean_test_nll_bits": nll,
                "information_gain_vs_word_bits": baseline_nll - nll,
                "deterministic_state_fraction_train": (
                    deterministic / states if states else 0.0
                ),
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "camp_a001_gpu_models.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "campaign": "CAMP-A001-0001-GPU",
        "starts": len(starts),
        "events": total_events,
        "word_length": args.word_length,
        "step_limit": args.step_limit,
        "device": device.name.strip(),
        "gpu_elapsed_ms": gpu_ns / 1_000_000,
        "wall_elapsed_s": time.perf_counter() - wall_start,
        "focused": args.focused,
        "workspace_sha256": hashlib.sha256(
            args.workspace_csv.read_bytes()
        ).hexdigest(),
    }
    (args.output_dir / "camp_a001_gpu_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report = [
        "CAMP-A001-0001-GPU PASS",
        f"device={summary['device']}",
        f"starts={summary['starts']}",
        f"events={summary['events']}",
        f"gpu_elapsed_ms={summary['gpu_elapsed_ms']:.3f}",
        f"wall_elapsed_s={summary['wall_elapsed_s']:.3f}",
        "",
        "MODELS BY TEST NLL",
    ]
    for row in sorted(rows, key=lambda r: r["mean_test_nll_bits"]):
        report.append(
            f"{row['model']} states={row['train_states']} "
            f"nll_bits={row['mean_test_nll_bits']:.9f} "
            f"gain_vs_word={row['information_gain_vs_word_bits']:.9f} "
            f"det_fraction={row['deterministic_state_fraction_train']:.9f}"
        )

    text = "\n".join(report) + "\n"
    (args.output_dir / "camp_a001_gpu_report.txt").write_text(
        text, encoding="utf-8"
    )
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
