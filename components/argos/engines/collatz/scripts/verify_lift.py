#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from typing import List, Optional, Tuple


def v2(n: int) -> int:
    """
    Valuation 2-adique de n.
    Retourne le plus grand k tel que 2^k divise n.
    """
    if n <= 0:
        raise ValueError("v2 exige n > 0")

    return (n & -n).bit_length() - 1


def compute_K_C(prefix_k: List[int]) -> Tuple[int, int]:
    """
    Calcule K_p et C_p pour un préfixe de valuations.

    K_0 = 0
    C_0 = 0

    C_{i+1} = 3 C_i + 2^{K_i}
    K_{i+1} = K_i + k_i
    """
    K = 0
    C = 0

    for k in prefix_k:
        if k <= 0:
            raise ValueError("Toutes les valuations doivent être >= 1")

        C = 3 * C + (1 << K)
        K += k

    return K, C


def inv_3_power(power: int, modulus: int) -> int:
    """
    Calcule 3^{-power} modulo modulus.

    modulus doit être une puissance de 2.
    Pour modulus = 1, l'anneau est trivial.
    """
    if modulus == 1:
        return 0

    a = pow(3, power, modulus)
    return pow(a, -1, modulus)


def raw_residue(prefix_k: List[int], extra_bits: int = 0) -> int:
    """
    Calcule le résidu brut :

        r ≡ -3^{-p} C_p mod 2^{K_p + extra_bits}

    Si extra_bits = 0 :
        résidu brut au module courant 2^{K_p}.

    Si extra_bits = q :
        relèvement brut au module 2^{K_p+q}.
    """
    p = len(prefix_k)
    K, C = compute_K_C(prefix_k)

    if extra_bits < 0:
        raise ValueError("extra_bits doit être >= 0")

    M = 1 << (K + extra_bits)

    if M == 1:
        return 0

    inv = inv_3_power(p, M)
    return (-inv * C) % M


@dataclass
class LiftCheck:
    p: int
    q: int
    K: int
    C: int
    r_p: int
    R_p_q: int
    a_p: int
    target: int
    s_p: int
    raw_accept: bool
    exact_accept: bool


def check_raw_lift_no_exact(prefix_k: List[int], q: int) -> bool:
    """
    Test brut de conservation de l'ancrage pour un q candidat.

    Renvoie True si :

        a_p ≡ 3^{-(p+1)} mod 2^q

    c'est-à-dire si s_p = 0 modulo 2^q.

    Cette fonction ne teste pas l'exactitude de q.
    """
    if q <= 0:
        raise ValueError("q doit être >= 1")

    p = len(prefix_k)
    K, _ = compute_K_C(prefix_k)

    M_old = 1 << K
    M_q = 1 << q

    r_p = raw_residue(prefix_k, extra_bits=0)
    R_p_q = raw_residue(prefix_k, extra_bits=q)

    if M_old == 1:
        a_p = R_p_q
    else:
        if (R_p_q - r_p) % M_old != 0:
            return False

        a_p = (R_p_q - r_p) // M_old

    a_p %= M_q

    target = inv_3_power(p + 1, M_q)

    return (a_p - target) % M_q == 0


def check_raw_lift(prefix_k: List[int], q: int) -> LiftCheck:
    """
    Vérifie le critère local corrigé de prolongement ancré.

    On calcule :

        R_p^{(q)} = r_p + a_p 2^{K_p}

    puis :

        s_p ≡ a_p - 3^{-(p+1)} mod 2^q

    Conservation brute du même représentant :

        s_p = 0

    Exactitude du q :

        raw_accept(q) == True
        raw_accept(q+1) == False

    Ce test ne détecte pas une chute.
    Il teste seulement la conservation de l'ancrage pour un q candidat.
    """
    if q <= 0:
        raise ValueError("q doit être >= 1")

    p = len(prefix_k)
    K, C = compute_K_C(prefix_k)

    M_old = 1 << K
    M_q = 1 << q

    r_p = raw_residue(prefix_k, extra_bits=0)
    R_p_q = raw_residue(prefix_k, extra_bits=q)

    if M_old == 1:
        a_p = R_p_q
    else:
        if (R_p_q - r_p) % M_old != 0:
            raise AssertionError("Erreur interne : relèvement incohérent")

        a_p = (R_p_q - r_p) // M_old

    a_p %= M_q

    target = inv_3_power(p + 1, M_q)
    s_p = (a_p - target) % M_q

    raw_accept = s_p == 0

    raw_accept_q_plus_1 = check_raw_lift_no_exact(prefix_k, q + 1)
    exact_accept = raw_accept and not raw_accept_q_plus_1

    return LiftCheck(
        p=p,
        q=q,
        K=K,
        C=C,
        r_p=r_p,
        R_p_q=R_p_q,
        a_p=a_p,
        target=target,
        s_p=s_p,
        raw_accept=raw_accept,
        exact_accept=exact_accept,
    )


def orbit_valuations(n0: int, depth: int) -> List[int]:
    """
    Produit les valuations réelles de l'orbite impaire accélérée issue de n0.
    """
    if n0 <= 0 or n0 % 2 == 0:
        raise ValueError("n0 doit être impair positif")

    if depth < 0:
        raise ValueError("depth doit être >= 0")

    n = n0
    ks: List[int] = []

    for _ in range(depth):
        x = 3 * n + 1
        k = v2(x)
        ks.append(k)
        n = x >> k

    return ks


def replay_prefix(n0: int, prefix_k: List[int]) -> Tuple[bool, int, Optional[int]]:
    """
    Rejoue un préfixe depuis n0.

    Retourne :
        ok_prefix,
        n_p,
        first_bad_index
    """
    if n0 <= 0 or n0 % 2 == 0:
        raise ValueError("n0 doit être impair positif")

    n = n0

    for i, k in enumerate(prefix_k):
        x = 3 * n + 1
        actual = v2(x)

        if actual != k:
            return False, n, i

        n = x >> k

    return True, n, None


def check_against_real_orbit(n0: int, depth: int, show_last: int = 20) -> None:
    """
    Vérifie que le q réel de l'orbite passe le test exact après ancrage brut.

    Attention :
    - ancrage exact du noyau v1 : 2^{K+1} > N ;
    - ici, comme on manipule le résidu brut modulo 2^K,
      le gel r_p = N exige 2^K > N.
    """
    ks = orbit_valuations(n0, depth)

    rows = []
    failures = []

    for p in range(0, depth):
        prefix = ks[:p]
        q = ks[p]

        K, _ = compute_K_C(prefix)

        raw_anchored = (1 << K) > n0
        exact_anchored = (1 << (K + 1)) > n0

        chk = check_raw_lift(prefix, q)

        ok_prefix, n_p, bad = replay_prefix(n0, prefix)
        if not ok_prefix:
            raise AssertionError(f"Préfixe réel invalide à p={p}, bad={bad}")

        actual_q = v2(3 * n_p + 1)

        if actual_q != q:
            raise AssertionError(
                f"Incohérence interne à p={p}: actual_q={actual_q}, q={q}"
            )

        if raw_anchored and not chk.exact_accept:
            failures.append((p, q, K, chk))

        rows.append({
            "p": p,
            "q": q,
            "K": K,
            "raw_anchored": raw_anchored,
            "exact_anchored": exact_anchored,
            "a_p": chk.a_p,
            "target": chk.target,
            "s_p": chk.s_p,
            "raw_accept": chk.raw_accept,
            "exact_accept": chk.exact_accept,
            "actual_q": actual_q,
        })

    print("=== REAL ORBIT LIFT CHECK ===")
    print(f"n0 = {n0}")
    print(f"depth = {depth}")
    print(f"failures_after_raw_anchor = {len(failures)}")
    print()

    if failures:
        print("=== FAILURES ===")
        for p, q, K, chk in failures[:20]:
            print(
                f"p={p} q={q} K={K} "
                f"a_p={chk.a_p} target={chk.target} "
                f"s_p={chk.s_p} exact={chk.exact_accept}"
            )
        print()

    print(f"=== LAST {show_last} STEPS ===")
    for row in rows[-show_last:]:
        print(
            f"p={row['p']:4d} "
            f"q={row['q']:2d} "
            f"K={row['K']:4d} "
            f"raw_anchor={str(row['raw_anchored']):5s} "
            f"a={row['a_p']:6d} "
            f"t={row['target']:6d} "
            f"s={row['s_p']:6d} "
            f"raw={str(row['raw_accept']):5s} "
            f"exact={str(row['exact_accept']):5s}"
        )


def anchored_continuation_profile(
    n0: int,
    depth: int,
    max_q: int = 12,
    show_last: int = 40,
) -> None:
    """
    Analyse les q candidats qui conserveraient l'ancrage sur le même entier N.

    Ce n'est pas un facteur de branchement libre.
    Pour une orbite réelle déjà ancrée, le q réel doit être retrouvé
    parmi les candidats admissibles, généralement de façon unique.
    """
    ks = orbit_valuations(n0, depth)

    rows = []

    for p in range(0, depth):
        prefix = ks[:p]

        if p == 0:
            continue

        real_q = ks[p]

        K, _ = compute_K_C(prefix)

        # Pour le résidu brut modulo 2^K, l'ancrage r_p = N est garanti
        # dès que 2^K > N.
        raw_anchored = (1 << K) > n0

        if not raw_anchored:
            continue

        candidates = []

        for q in range(1, max_q + 1):
            chk = check_raw_lift(prefix, q)

            if chk.exact_accept:
                candidates.append(q)

        rows.append({
            "p": p,
            "K": K,
            "real_q": real_q,
            "candidates": candidates,
            "count": len(candidates),
            "real_in_candidates": real_q in candidates,
        })

    print("=== ANCHORED CONTINUATION PROFILE ===")
    print(f"n0 = {n0}")
    print(f"depth = {depth}")
    print(f"max_q = {max_q}")
    print(f"anchored_steps = {len(rows)}")
    print()

    counts = {}
    for row in rows:
        counts[row["count"]] = counts.get(row["count"], 0) + 1

    print("=== CANDIDATE COUNTS ===")
    for count in sorted(counts):
        print(f"candidate_count={count}: {counts[count]}")

    bad = [r for r in rows if not r["real_in_candidates"]]

    print()
    print(f"real_q_missing = {len(bad)}")
    print()

    if bad:
        print("=== REAL q MISSING CASES ===")
        for row in bad[:20]:
            print(
                f"p={row['p']:4d} "
                f"K={row['K']:4d} "
                f"real_q={row['real_q']:2d} "
                f"count={row['count']:2d} "
                f"candidates={row['candidates']}"
            )
        print()

    print(f"=== LAST {show_last} ANCHORED STEPS ===")
    for row in rows[-show_last:]:
        print(
            f"p={row['p']:4d} "
            f"K={row['K']:4d} "
            f"real_q={row['real_q']:2d} "
            f"count={row['count']:2d} "
            f"candidates={row['candidates']}"
        )


def anchored_agreement_export(
    n0: int,
    depth: int,
    max_q: int,
    output_csv: str,
) -> None:
    """
    Exporte, pour chaque étape ancrée, le nombre maximal de bits faibles
    sur lesquels le relèvement a_p coïncide avec 3^{-(p+1)}.

    agreement_bits(p) = max q tel que raw_accept(q) est vrai.

    Pour une orbite réelle, on s'attend à :

        agreement_bits(p) = k_p

    tant que max_q est assez grand.
    """
    ks = orbit_valuations(n0, depth)

    rows = []

    mismatch = 0
    anchored_count = 0

    for p in range(1, depth):
        prefix = ks[:p]
        real_q = ks[p]

        K, C = compute_K_C(prefix)

        raw_anchored = (1 << K) > n0

        if not raw_anchored:
            continue

        anchored_count += 1

        agreement_bits = 0
        raw_accepts = []
        exact_candidates = []

        for q in range(1, max_q + 1):
            chk = check_raw_lift(prefix, q)

            if chk.raw_accept:
                raw_accepts.append(q)
                agreement_bits = q

            if chk.exact_accept:
                exact_candidates.append(q)

        if agreement_bits != real_q:
            mismatch += 1

        rows.append({
            "p": p,
            "K": K,
            "real_q": real_q,
            "agreement_bits": agreement_bits,
            "raw_accepts": ";".join(map(str, raw_accepts)),
            "exact_candidates": ";".join(map(str, exact_candidates)),
            "match": agreement_bits == real_q,
            "C": C,
        })

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fields = [
            "p",
            "K",
            "real_q",
            "agreement_bits",
            "raw_accepts",
            "exact_candidates",
            "match",
            "C",
        ]

        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    hist = {}
    for row in rows:
        q = row["agreement_bits"]
        hist[q] = hist.get(q, 0) + 1

    print("=== ANCHORED AGREEMENT EXPORT ===")
    print(f"n0 = {n0}")
    print(f"depth = {depth}")
    print(f"max_q = {max_q}")
    print(f"anchored_steps = {anchored_count}")
    print(f"mismatch = {mismatch}")
    print(f"output_csv = {output_csv}")
    print()

    print("=== AGREEMENT_BITS HISTOGRAM ===")
    for q in sorted(hist):
        print(f"agreement_bits={q}: {hist[q]}")


def scan_candidates_for_prefix(prefix_k: List[int], max_q: int) -> None:
    """
    Pour un préfixe donné, affiche les q qui conservent exactement l'ancrage brut.
    """
    print("=== CANDIDATE q CHECK ===")
    print(f"prefix length p = {len(prefix_k)}")

    K, C = compute_K_C(prefix_k)

    print(f"K = {K}")
    print(f"C = {C}")
    print()

    for q in range(1, max_q + 1):
        chk = check_raw_lift(prefix_k, q)

        if chk.raw_accept or chk.exact_accept:
            print(
                f"q={q:2d} "
                f"a={chk.a_p} "
                f"target={chk.target} "
                f"s={chk.s_p} "
                f"raw={chk.raw_accept} "
                f"exact={chk.exact_accept}"
            )


def self_test() -> None:
    """
    Tests minimaux non probabilistes.
    """
    print("=== SELF TEST ===")

    for n0, depth in [
        (27, 40),
        (35655, 90),
        (2788008987, 282),
    ]:
        print()
        check_against_real_orbit(n0=n0, depth=depth, show_last=5)

    print()
    print("SELF TEST DONE")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vérificateur du critère local corrigé de prolongement ancré."
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic self tests",
    )

    parser.add_argument(
        "--n0",
        type=int,
        default=None,
        help="Entier impair positif à analyser",
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=100,
        help="Profondeur de l'orbite réelle à analyser",
    )

    parser.add_argument(
        "--show-last",
        type=int,
        default=20,
        help="Nombre de dernières lignes à afficher",
    )

    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="Préfixe de valuations, ex: 1,2,1,1,3",
    )

    parser.add_argument(
        "--max-q",
        type=int,
        default=12,
        help="q maximal à tester pour les candidats",
    )

    parser.add_argument(
        "--anchored-profile",
        action="store_true",
        help="Run anchored continuation profile",
    )

    parser.add_argument(
        "--agreement-csv",
        type=str,
        default=None,
        help="Export anchored agreement_bits profile to CSV",
    )

    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.n0 is not None and args.agreement_csv is not None:
        anchored_agreement_export(
            n0=args.n0,
            depth=args.depth,
            max_q=args.max_q,
            output_csv=args.agreement_csv,
        )
        return

    if args.n0 is not None and args.anchored_profile:
        anchored_continuation_profile(
            n0=args.n0,
            depth=args.depth,
            max_q=args.max_q,
            show_last=args.show_last,
        )
        return

    if args.n0 is not None:
        check_against_real_orbit(
            n0=args.n0,
            depth=args.depth,
            show_last=args.show_last,
        )
        return

    if args.prefix is not None:
        prefix_k = [int(x.strip()) for x in args.prefix.split(",") if x.strip()]
        scan_candidates_for_prefix(prefix_k, args.max_q)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
