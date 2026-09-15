#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class Report:
    n0: int
    exit_found: bool
    exit_depth: int
    exit_k: int
    K: int
    p_stab: Optional[int]
    L: int
    before_exit: int
    after_exit: int
    max_orbit: int
    strong_drop: bool


def v2(n: int) -> int:
    """
    Valuation 2-adique de n.
    Retourne le plus grand k tel que 2^k divise n.
    """
    if n <= 0:
        raise ValueError("v2(n) exige n > 0")

    return (n & -n).bit_length() - 1


def analyze_n(n0: int, max_depth: int) -> Report:
    """
    Analyse la trajectoire impaire accélérée issue de n0.

    Calcule :
    - première sortie du couloir dangereux : 2^K > 3^p
    - p_stab : première profondeur où 2^(K+1) > n0
    - L(n0) = max(0, exit_depth - p_stab)
    - chute sous n0 à la sortie
    """
    if n0 <= 0 or n0 % 2 == 0:
        raise ValueError("n0 doit être impair positif")

    n = n0
    K = 0
    p_stab: Optional[int] = None
    max_orbit = n0
    pow3 = 1

    for p in range(1, max_depth + 1):
        before = n

        x = 3 * n + 1
        k = v2(x)

        K += k
        n = x >> k

        if n > max_orbit:
            max_orbit = n

        pow3 *= 3

        # Stabilisation exacte :
        # premier p tel que 2^(K+1) > n0.
        if p_stab is None and (1 << (K + 1)) > n0:
            p_stab = p

        # Sortie du couloir dangereux :
        # 2^K > 3^p.
        if (1 << K) > pow3:
            L = 0 if p_stab is None else max(0, p - p_stab)

            return Report(
                n0=n0,
                exit_found=True,
                exit_depth=p,
                exit_k=k,
                K=K,
                p_stab=p_stab,
                L=L,
                before_exit=before,
                after_exit=n,
                max_orbit=max_orbit,
                strong_drop=(n < n0),
            )

    return Report(
        n0=n0,
        exit_found=False,
        exit_depth=max_depth + 1,
        exit_k=-1,
        K=K,
        p_stab=p_stab,
        L=0,
        before_exit=0,
        after_exit=n,
        max_orbit=max_orbit,
        strong_drop=False,
    )


def report_to_row(report: Report, record_type: str) -> dict:
    log2_n0 = math.log2(report.n0) if report.n0 > 1 else None

    return {
        "type": record_type,
        "n0": report.n0,
        "exit_found": report.exit_found,
        "exit_depth": report.exit_depth,
        "p_stab": report.p_stab,
        "L": report.L,
        "exit_k": report.exit_k,
        "K": report.K,
        "before_exit": report.before_exit,
        "after_exit": report.after_exit,
        "max_orbit": report.max_orbit,
        "strong_drop": report.strong_drop,
        "log2_n0": log2_n0,
        "exit_over_log2_n0": (
            report.exit_depth / log2_n0
            if log2_n0 and report.exit_found
            else None
        ),
        "L_over_log2_n0": (
            report.L / log2_n0
            if log2_n0
            else None
        ),
    }


def write_checkpoint(
    checkpoint_path: str,
    current_n0: int,
    best_R: Optional[Report],
    best_L: Optional[Report],
    started_at: float,
) -> None:
    elapsed = time.time() - started_at

    with open(checkpoint_path, "w", encoding="utf-8") as f:
        f.write("{\n")
        f.write(f'  "current_n0": {current_n0},\n')
        f.write(f'  "elapsed_seconds": {elapsed:.3f},\n')

        if best_R is not None:
            f.write('  "best_R": {\n')
            f.write(f'    "n0": {best_R.n0},\n')
            f.write(f'    "exit_depth": {best_R.exit_depth},\n')
            f.write(f'    "p_stab": {best_R.p_stab},\n')
            f.write(f'    "L": {best_R.L},\n')
            f.write(f'    "exit_k": {best_R.exit_k},\n')
            f.write(f'    "K": {best_R.K},\n')
            f.write(f'    "strong_drop": {str(best_R.strong_drop).lower()}\n')
            f.write("  },\n")
        else:
            f.write('  "best_R": null,\n')

        if best_L is not None:
            f.write('  "best_L": {\n')
            f.write(f'    "n0": {best_L.n0},\n')
            f.write(f'    "exit_depth": {best_L.exit_depth},\n')
            f.write(f'    "p_stab": {best_L.p_stab},\n')
            f.write(f'    "L": {best_L.L},\n')
            f.write(f'    "exit_k": {best_L.exit_k},\n')
            f.write(f'    "K": {best_L.K},\n')
            f.write(f'    "strong_drop": {str(best_L.strong_drop).lower()}\n')
            f.write("  }\n")
        else:
            f.write('  "best_L": null\n')

        f.write("}\n")


def scan_records(
    max_n: int,
    max_depth: int,
    output_csv: str,
    checkpoint_path: str,
    progress_every: int,
    checkpoint_every: int,
) -> None:
    best_R: Optional[Report] = None
    best_L: Optional[Report] = None

    started_at = time.time()
    processed = 0

    fields = [
        "type",
        "n0",
        "exit_found",
        "exit_depth",
        "p_stab",
        "L",
        "exit_k",
        "K",
        "before_exit",
        "after_exit",
        "max_orbit",
        "strong_drop",
        "log2_n0",
        "exit_over_log2_n0",
        "L_over_log2_n0",
    ]

    powers = []
    x = 10
    while x <= max_n:
        powers.append(x)
        x *= 10

    next_power_index = 0

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for n0 in range(1, max_n + 1, 2):
            processed += 1
            report = analyze_n(n0, max_depth=max_depth)

            if best_R is None or report.exit_depth > best_R.exit_depth:
                best_R = report
                writer.writerow(report_to_row(report, "R_RECORD"))
                f.flush()

                print(
                    f"[R] n0={report.n0} "
                    f"exit={report.exit_depth} "
                    f"p_stab={report.p_stab} "
                    f"L={report.L} "
                    f"k={report.exit_k} "
                    f"K={report.K} "
                    f"drop={report.strong_drop}",
                    file=sys.stderr,
                )

            if best_L is None or report.L > best_L.L:
                best_L = report
                writer.writerow(report_to_row(report, "L_RECORD"))
                f.flush()

                print(
                    f"[L] n0={report.n0} "
                    f"exit={report.exit_depth} "
                    f"p_stab={report.p_stab} "
                    f"L={report.L} "
                    f"k={report.exit_k} "
                    f"K={report.K} "
                    f"drop={report.strong_drop}",
                    file=sys.stderr,
                )

            while next_power_index < len(powers) and n0 >= powers[next_power_index]:
                N = powers[next_power_index]
                elapsed = time.time() - started_at
                rate = processed / elapsed if elapsed > 0 else 0.0

                print("", file=sys.stderr)
                print(f"CHECKPOINT N={N}", file=sys.stderr)
                print(f"elapsed={elapsed:.2f}s rate={rate:.2f} odd/s", file=sys.stderr)

                if best_R is not None:
                    print(
                        f"Best R: n0={best_R.n0} "
                        f"exit={best_R.exit_depth} "
                        f"p_stab={best_R.p_stab} "
                        f"L={best_R.L} "
                        f"drop={best_R.strong_drop}",
                        file=sys.stderr,
                    )

                if best_L is not None:
                    print(
                        f"Best L: n0={best_L.n0} "
                        f"exit={best_L.exit_depth} "
                        f"p_stab={best_L.p_stab} "
                        f"L={best_L.L} "
                        f"drop={best_L.strong_drop}",
                        file=sys.stderr,
                    )

                write_checkpoint(
                    checkpoint_path=checkpoint_path,
                    current_n0=n0,
                    best_R=best_R,
                    best_L=best_L,
                    started_at=started_at,
                )

                next_power_index += 1

            if progress_every > 0 and n0 % progress_every == 1:
                elapsed = time.time() - started_at
                rate = processed / elapsed if elapsed > 0 else 0.0

                print(
                    f"progress n0={n0} elapsed={elapsed:.2f}s rate={rate:.2f} odd/s",
                    file=sys.stderr,
                )

            if checkpoint_every > 0 and n0 % checkpoint_every == 1:
                write_checkpoint(
                    checkpoint_path=checkpoint_path,
                    current_n0=n0,
                    best_R=best_R,
                    best_L=best_L,
                    started_at=started_at,
                )

    write_checkpoint(
        checkpoint_path=checkpoint_path,
        current_n0=max_n,
        best_R=best_R,
        best_L=best_L,
        started_at=started_at,
    )

    elapsed = time.time() - started_at
    rate = processed / elapsed if elapsed > 0 else 0.0

    print("", file=sys.stderr)
    print("DONE", file=sys.stderr)
    print(f"elapsed={elapsed:.2f}s rate={rate:.2f} odd/s", file=sys.stderr)

    if best_R is not None:
        print(
            f"Final Best R: n0={best_R.n0} "
            f"exit={best_R.exit_depth} "
            f"p_stab={best_R.p_stab} "
            f"L={best_R.L} "
            f"drop={best_R.strong_drop}",
            file=sys.stderr,
        )

    if best_L is not None:
        print(
            f"Final Best L: n0={best_L.n0} "
            f"exit={best_L.exit_depth} "
            f"p_stab={best_L.p_stab} "
            f"L={best_L.L} "
            f"drop={best_L.strong_drop}",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan des records R(N) et L(N) pour la dynamique impaire accélérée de Collatz."
    )

    parser.add_argument(
        "--max-n",
        type=int,
        default=1_000_000,
        help="borne maximale du scan",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=3000,
        help="profondeur maximale par trajectoire",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="records.csv",
        help="fichier CSV des records",
    )

    parser.add_argument(
        "--checkpoint",
        type=str,
        default="checkpoint_latest.json",
        help="fichier checkpoint JSON",
    )

    parser.add_argument(
        "--progress-every",
        type=int,
        default=1_000_001,
        help="affichage progression tous les N",
    )

    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=10_000_001,
        help="écriture checkpoint tous les N",
    )

    args = parser.parse_args()

    scan_records(
        max_n=args.max_n,
        max_depth=args.max_depth,
        output_csv=args.output,
        checkpoint_path=args.checkpoint,
        progress_every=args.progress_every,
        checkpoint_every=args.checkpoint_every,
    )


if __name__ == "__main__":
    main()
