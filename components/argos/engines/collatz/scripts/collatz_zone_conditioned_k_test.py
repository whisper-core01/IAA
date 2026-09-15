#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence

LOG2_3 = math.log2(3.0)
ALPHA = 0.5


@dataclass(frozen=True)
class Event:
    trajectory_id: int
    step: int
    word: tuple[int, ...]
    debt_out: float
    debt_bin: int
    zone: str
    k_next: int


def v2(x: int) -> int:
    if x <= 0:
        raise ValueError("v2 exige x > 0")
    k = 0
    while (x & 1) == 0:
        x >>= 1
        k += 1
    return k


def oddify(n: int) -> int:
    if n <= 0:
        raise ValueError("n doit être positif")
    while (n & 1) == 0:
        n >>= 1
    return n


def odd_step(n: int) -> tuple[int, int]:
    x = 3 * n + 1
    k = v2(x)
    return x >> k, k


def zone_of(start: int, current: int) -> str:
    r = math.log2(current / start)
    if r < -1.0:
        return "BELOW_HALF"
    if r < 0.0:
        return "BELOW_START"
    if r < 1.0:
        return "LOW_ASCENT"
    if r < 2.0:
        return "HIGH_ASCENT"
    return "EXTREME"


def debt_bucket(x: float, width: float) -> int:
    return math.floor(x / width)


def make_events(
    trajectory_id: int,
    raw_start: int,
    word_length: int,
    debt_bin_width: float,
    step_limit: int,
) -> Iterable[Event]:
    start = oddify(raw_start)
    n = start
    debt = 0.0
    ks: list[int] = []
    states: list[int] = [n]
    debts: list[float] = []

    for _ in range(step_limit):
        if n == 1:
            break
        n, k = odd_step(n)
        debt += LOG2_3 - k
        ks.append(k)
        states.append(n)
        debts.append(debt)

    for end in range(word_length - 1, len(ks) - 1):
        begin = end - word_length + 1
        yield Event(
            trajectory_id=trajectory_id,
            step=end,
            word=tuple(ks[begin:end + 1]),
            debt_out=debts[end],
            debt_bin=debt_bucket(debts[end], debt_bin_width),
            zone=zone_of(start, states[end + 1]),
            k_next=ks[end + 1],
        )


def detect_start_column(fieldnames: Sequence[str]) -> str:
    by_lower = {x.lower(): x for x in fieldnames}
    for candidate in ("n", "start", "start_n", "input", "value", "seed"):
        if candidate in by_lower:
            return by_lower[candidate]
    raise RuntimeError(
        "Colonne de départ introuvable. Colonnes présentes: "
        + ", ".join(fieldnames)
    )


def load_starts(path: Path, max_rows: int | None) -> list[int]:
    result: list[int] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError("CSV sans en-tête")
        column = detect_start_column(reader.fieldnames)
        for i, row in enumerate(reader):
            if max_rows is not None and i >= max_rows:
                break
            raw = (row.get(column) or "").strip()
            if not raw:
                continue
            try:
                n = int(raw)
            except ValueError as exc:
                raise RuntimeError(
                    f"Valeur invalide ligne {i + 2}, colonne {column}: {raw!r}"
                ) from exc
            if n > 0:
                result.append(n)
    if not result:
        raise RuntimeError("Aucun entier positif trouvé dans le CSV")
    return result


def deterministic_split(event: Event, test_fraction: float) -> bool:
    payload = f"{event.trajectory_id}:{event.step}".encode()
    h = hashlib.sha256(payload).digest()
    u = int.from_bytes(h[:8], "big") / 2**64
    return u < test_fraction


def base_key(e: Event):
    return e.word, e.debt_bin


def zone_key(e: Event):
    return e.word, e.debt_bin, e.zone


def build_counts(events: Sequence[Event], zonal: bool):
    table = defaultdict(Counter)
    global_counts = Counter()
    for e in events:
        key = zone_key(e) if zonal else base_key(e)
        table[key][e.k_next] += 1
        global_counts[e.k_next] += 1
    return table, global_counts


def mean_nll_bits(train: Sequence[Event], test: Sequence[Event], zonal: bool) -> float:
    table, global_counts = build_counts(train, zonal)
    labels = sorted(global_counts)
    if not labels:
        raise RuntimeError("Ensemble d'entraînement vide")
    total = 0.0
    for e in test:
        key = zone_key(e) if zonal else base_key(e)
        counts = table.get(key, global_counts)
        denom = sum(counts.values()) + ALPHA * len(labels)
        p = (counts.get(e.k_next, 0) + ALPHA) / denom
        total -= math.log2(p)
    return total / len(test)


def shared_context_filter(events: Sequence[Event]) -> list[Event]:
    zones = defaultdict(set)
    for e in events:
        zones[base_key(e)].add(e.zone)
    admissible = {k for k, z in zones.items() if len(z) >= 2}
    return [e for e in events if base_key(e) in admissible]


def permuted_train(train: Sequence[Event], rng: random.Random) -> list[Event]:
    groups = defaultdict(list)
    for i, e in enumerate(train):
        groups[base_key(e)].append(i)

    result = list(train)
    for indices in groups.values():
        shuffled = [train[i].zone for i in indices]
        rng.shuffle(shuffled)
        for i, z in zip(indices, shuffled):
            e = train[i]
            result[i] = Event(
                trajectory_id=e.trajectory_id,
                step=e.step,
                word=e.word,
                debt_out=e.debt_out,
                debt_bin=e.debt_bin,
                zone=z,
                k_next=e.k_next,
            )
    return result


def write_events(path: Path, events: Sequence[Event]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "trajectory_id", "step", "word", "debt_out",
            "debt_bin", "zone", "k_next"
        ])
        for e in events:
            writer.writerow([
                e.trajectory_id,
                e.step,
                "-".join(map(str, e.word)),
                f"{e.debt_out:.12f}",
                e.debt_bin,
                e.zone,
                e.k_next,
            ])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace_csv", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--word-length", type=int, default=6)
    ap.add_argument("--debt-bin-width", type=float, default=0.5)
    ap.add_argument("--step-limit", type=int, default=1000)
    ap.add_argument("--max-rows", type=int, default=None)
    ap.add_argument("--test-fraction", type=float, default=0.25)
    ap.add_argument("--permutations", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260729)
    args = ap.parse_args()

    if args.word_length < 1:
        raise RuntimeError("--word-length doit être >= 1")
    if args.debt_bin_width <= 0:
        raise RuntimeError("--debt-bin-width doit être > 0")
    if not (0.05 <= args.test_fraction <= 0.5):
        raise RuntimeError("--test-fraction doit être entre 0.05 et 0.5")
    if args.permutations < 10:
        raise RuntimeError("--permutations doit être >= 10")

    starts = load_starts(args.workspace_csv, args.max_rows)
    events: list[Event] = []
    for tid, n in enumerate(starts):
        events.extend(make_events(
            tid, n, args.word_length, args.debt_bin_width, args.step_limit
        ))

    events = shared_context_filter(events)
    if len(events) < 500:
        raise RuntimeError(
            f"Échantillon insuffisant après filtrage des contextes partagés: {len(events)}"
        )

    train = [e for e in events if not deterministic_split(e, args.test_fraction)]
    test = [e for e in events if deterministic_split(e, args.test_fraction)]
    if not train or not test:
        raise RuntimeError("Découpage train/test vide")

    base_nll = mean_nll_bits(train, test, zonal=False)
    zone_nll = mean_nll_bits(train, test, zonal=True)
    observed_gain = base_nll - zone_nll

    rng = random.Random(args.seed)
    permuted_gains: list[float] = []
    for _ in range(args.permutations):
        ptrain = permuted_train(train, rng)
        perm_zone_nll = mean_nll_bits(ptrain, test, zonal=True)
        permuted_gains.append(base_nll - perm_zone_nll)

    p_value = (
        1 + sum(g >= observed_gain for g in permuted_gains)
    ) / (len(permuted_gains) + 1)

    if observed_gain > 0 and p_value < 0.05:
        verdict = "SUPPORTED"
    elif observed_gain <= 0 and p_value >= 0.05:
        verdict = "NOT_SUPPORTED"
    else:
        verdict = "INCONCLUSIVE"

    args.output_dir.mkdir(parents=True, exist_ok=True)
    events_csv = args.output_dir / "collatz_zone_conditioned_k_events_v1.csv"
    result_json = args.output_dir / "collatz_zone_conditioned_k_test_v1.json"
    result_txt = args.output_dir / "collatz_zone_conditioned_k_test_v1.txt"

    write_events(events_csv, events)

    payload = {
        "campaign_kind": "COLLATZ_ZONE_CONDITIONED_K_TEST_V1",
        "workspace_csv": str(args.workspace_csv.resolve()),
        "workspace_sha256": hashlib.sha256(args.workspace_csv.read_bytes()).hexdigest(),
        "starts": len(starts),
        "events": len(events),
        "train_events": len(train),
        "test_events": len(test),
        "word_length": args.word_length,
        "debt_bin_width": args.debt_bin_width,
        "step_limit": args.step_limit,
        "permutations": args.permutations,
        "base_nll_bits": base_nll,
        "zone_nll_bits": zone_nll,
        "information_gain_bits_per_event": observed_gain,
        "permutation_p_value": p_value,
        "verdict": verdict,
        "zone_definition": {
            "BELOW_HALF": "log2(current/start) < -1",
            "BELOW_START": "-1 <= log2(current/start) < 0",
            "LOW_ASCENT": "0 <= log2(current/start) < 1",
            "HIGH_ASCENT": "1 <= log2(current/start) < 2",
            "EXTREME": "log2(current/start) >= 2",
        },
    }

    result_json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    line = (
        "COLLATZ_ZONE_CONDITIONED_K_TEST_"
        f"{verdict} "
        f"starts={len(starts)} "
        f"events={len(events)} "
        f"train={len(train)} "
        f"test={len(test)} "
        f"base_nll_bits={base_nll:.9f} "
        f"zone_nll_bits={zone_nll:.9f} "
        f"information_gain_bits_per_event={observed_gain:.9f} "
        f"permutation_p_value={p_value:.9f} "
        f"permutations={args.permutations}"
    )
    result_txt.write_text(line + "\n", encoding="utf-8")
    print(line)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            f"COLLATZ_ZONE_CONDITIONED_K_TEST_FAIL error={exc}",
            file=sys.stderr,
        )
        raise SystemExit(1)

