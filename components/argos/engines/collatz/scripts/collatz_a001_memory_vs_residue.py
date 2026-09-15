#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence

ALPHA = 0.5


def v2(x: int) -> int:
    if x <= 0:
        raise ValueError("v2 exige x > 0")
    return (x & -x).bit_length() - 1


def oddify(n: int) -> int:
    if n <= 0:
        raise ValueError("n doit être positif")
    return n >> v2(n)


def odd_step(n: int) -> tuple[int, int]:
    x = 3 * n + 1
    k = v2(x)
    return x >> k, k


def detect_start_column(fieldnames: Sequence[str]) -> str:
    by_lower = {name.lower(): name for name in fieldnames}
    for candidate in ("n", "start", "start_n", "input", "value", "seed"):
        if candidate in by_lower:
            return by_lower[candidate]
    raise RuntimeError("Colonne de départ introuvable: " + ", ".join(fieldnames))


def load_starts(path: Path, max_rows: int | None) -> list[int]:
    starts: list[int] = []
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
            try:
                n = int(raw)
            except ValueError as exc:
                raise RuntimeError(
                    f"Valeur invalide ligne {row_index + 2}, colonne {column}: {raw!r}"
                ) from exc
            if n > 0:
                starts.append(n)
    if not starts:
        raise RuntimeError("Aucun entier positif trouvé")
    return starts


def make_events(raw_start: int, word_length: int, step_limit: int):
    n = oddify(raw_start)
    ks: list[int] = []
    states: list[int] = [n]
    for _ in range(step_limit):
        if n == 1:
            break
        n, k = odd_step(n)
        ks.append(k)
        states.append(n)
    for end in range(word_length - 1, len(ks) - 1):
        begin = end - word_length + 1
        yield end, states[end + 1], tuple(ks[begin : end + 1]), ks[end + 1]


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


def main() -> int:
    ap = argparse.ArgumentParser(
        description="CAMP-A001-0001: mémoire contre résidu arithmétique."
    )
    ap.add_argument("workspace_csv", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--word-length", type=int, default=6)
    ap.add_argument("--step-limit", type=int, default=1000)
    ap.add_argument("--max-memory-words", type=int, default=6)
    ap.add_argument("--residue-powers", default="1,2,3,4,5,6,8,10,12")
    ap.add_argument("--max-rows", type=int)
    ap.add_argument("--test-fraction", type=float, default=0.25)
    args = ap.parse_args()

    if args.word_length < 1 or args.max_memory_words < 1:
        raise RuntimeError("Les longueurs doivent être >= 1")
    if not 0.05 <= args.test_fraction <= 0.5:
        raise RuntimeError("--test-fraction doit être entre 0.05 et 0.5")

    residue_powers = sorted({int(x) for x in args.residue_powers.split(",") if x})
    starts = load_starts(args.workspace_csv, args.max_rows)

    specs: list[tuple[str, str, int, int | None]] = [("word", "word", 1, None)]
    for p in residue_powers:
        specs.append((f"word_mod_2^{p}", "residue", 1, 1 << p))
    for depth in range(2, args.max_memory_words + 1):
        specs.append((f"memory_{depth}_words", "memory", depth, None))
        for p in residue_powers:
            specs.append(
                (f"memory_{depth}_words_mod_2^{p}", "both", depth, 1 << p)
            )

    train = {name: defaultdict(Counter) for name, _, _, _ in specs}
    tests: dict[str, list[tuple[object, int]]] = defaultdict(list)
    global_train: Counter[int] = Counter()
    word_counts: dict[tuple[int, ...], Counter[int]] = defaultdict(Counter)
    total_events = 0

    for trajectory_id, start in enumerate(starts):
        events = list(make_events(start, args.word_length, args.step_limit))
        words = [event[2] for event in events]
        for index, (step, n_current, word, k_next) in enumerate(events):
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
                    key = (word, n_current % modulus)
                elif mode == "memory":
                    key = memory
                else:
                    key = (memory, n_current % modulus)

                if test:
                    tests[name].append((key, k_next))
                else:
                    train[name][key][k_next] += 1

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
                "deterministic_state_fraction_train": deterministic / states if states else 0.0,
                "mean_successors_per_state_train": (
                    sum(len(c) for c in table.values()) / states if states else 0.0
                ),
                "max_successors_per_state_train": max((len(c) for c in table.values()), default=0),
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    with (args.output_dir / "camp_a001_0001_models.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    transition_rows = []
    for word, successors in sorted(
        word_counts.items(), key=lambda item: (-sum(item[1].values()), item[0])
    ):
        total = sum(successors.values())
        transition_rows.append(
            {
                "word": "-".join(map(str, word)),
                "occurrences": total,
                "successor_count": len(successors),
                "successor_entropy_bits": entropy_bits(successors),
                "successors": ";".join(
                    f"{k}:{count}:{count / total:.12f}"
                    for k, count in sorted(successors.items())
                ),
            }
        )

    with (args.output_dir / "camp_a001_0001_word_transitions.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(transition_rows[0]))
        writer.writeheader()
        writer.writerows(transition_rows)

    summary = {
        "campaign": "CAMP-A001-0001",
        "projection": "accelerated_odd_collatz_k_word",
        "starts": len(starts),
        "events": total_events,
        "word_length": args.word_length,
        "step_limit": args.step_limit,
        "distinct_words": len(word_counts),
        "distinct_word_to_k_transitions": sum(len(c) for c in word_counts.values()),
        "workspace_sha256": hashlib.sha256(args.workspace_csv.read_bytes()).hexdigest(),
    }
    (args.output_dir / "camp_a001_0001_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    report = [
        "CAMP-A001-0001 PASS",
        f"starts={summary['starts']}",
        f"events={summary['events']}",
        f"distinct_words={summary['distinct_words']}",
        f"distinct_word_to_k_transitions={summary['distinct_word_to_k_transitions']}",
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
    (args.output_dir / "camp_a001_0001_report.txt").write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
