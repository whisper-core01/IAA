#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from collections import Counter


LOG2_3 = math.log2(3)


def v2(n: int) -> int:
    return (n & -n).bit_length() - 1


def analyze(n0: int, max_depth: int, output_csv: str) -> None:
    n = n0
    K = 0
    max_orbit = n0
    max_pos = 0
    p_stab = None
    pow3 = 1

    rows = []
    ks = []

    for p in range(1, max_depth + 1):
        before = n
        x = 3 * n + 1
        k = v2(x)
        ks.append(k)

        K += k
        n = x >> k
        pow3 *= 3

        if n > max_orbit:
            max_orbit = n
            max_pos = p

        if p_stab is None and (1 << (K + 1)) > n0:
            p_stab = p

        dangerous = (1 << K) <= pow3
        exit_now = not dangerous
        anchored = p_stab is not None

        ratio = K / p
        delta = ratio - LOG2_3

        rows.append({
            "p": p,
            "before": before,
            "k": k,
            "after": n,
            "K": K,
            "K_over_p": ratio,
            "delta_to_log2_3": delta,
            "dangerous": dangerous,
            "anchored": anchored,
            "p_stab": p_stab,
            "max_so_far": max_orbit,
            "is_new_max": p == max_pos,
            "exit_now": exit_now,
            "drop_under_n0": n < n0,
        })

        if exit_now:
            break

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fields = [
            "p",
            "before",
            "k",
            "after",
            "K",
            "K_over_p",
            "delta_to_log2_3",
            "dangerous",
            "anchored",
            "p_stab",
            "max_so_far",
            "is_new_max",
            "exit_now",
            "drop_under_n0",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    dist = Counter(ks)
    exit_row = rows[-1]

    print("=== CHAMPION ANALYSIS ===")
    print(f"n0 = {n0}")
    print(f"exit_depth = {exit_row['p']}")
    print(f"p_stab = {p_stab}")
    print(f"L = {exit_row['p'] - p_stab if p_stab is not None else 0}")
    print(f"exit_k = {exit_row['k']}")
    print(f"K_exit = {exit_row['K']}")
    print(f"K/p = {exit_row['K_over_p']}")
    print(f"log2(3) = {LOG2_3}")
    print(f"delta = {exit_row['delta_to_log2_3']}")
    print(f"before_exit = {exit_row['before']}")
    print(f"after_exit = {exit_row['after']}")
    print(f"drop_under_n0 = {exit_row['drop_under_n0']}")
    print(f"max_orbit = {max_orbit}")
    print(f"max_orbit_position = {max_pos}")
    print()

    print("=== k DISTRIBUTION ===")
    for k in sorted(dist):
        print(f"k={k}: {dist[k]}")

    print()
    print("=== positions k >= 3 ===")
    print(",".join(str(i + 1) for i, k in enumerate(ks) if k >= 3))

    print()
    print("=== positions k >= 4 ===")
    print(",".join(str(i + 1) for i, k in enumerate(ks) if k >= 4))

    print()
    print("=== positions k >= 6 ===")
    print(",".join(str(i + 1) for i, k in enumerate(ks) if k >= 6))

    print()
    print("=== last 25 steps ===")
    for row in rows[-25:]:
        print(
            f"p={row['p']:3d} "
            f"k={row['k']:2d} "
            f"K={row['K']:3d} "
            f"K/p={row['K_over_p']:.6f} "
            f"before={row['before']} "
            f"after={row['after']} "
            f"exit={row['exit_now']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n0", type=int, required=True)
    parser.add_argument("--max-depth", type=int, default=1000)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    analyze(args.n0, args.max_depth, args.output)


if __name__ == "__main__":
    main()
