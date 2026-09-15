# collatz_scanner/src/vmean_scale_scan.py

import math
from trajectory import extract_blocks


LOG2_3 = math.log2(3)


def V(b):
    return (b["L_j"] + 1) * LOG2_3 - (b["L_j"] + b["k_rupture"])


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if not xs:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def corr(xs, ys):
    if len(xs) < 2:
        return 0.0
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else 0.0


def linreg(xs, ys):
    mx, my = mean(xs), mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return 0.0, my
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    b = my - a * mx
    return a, b


def analyze_scale(N_max):
    rows = []

    for N in range(1, N_max + 1, 2):
        blocks = extract_blocks(N)
        if len(blocks) < 3:
            continue

        vs = [V(b) for b in blocks]
        vm = mean(vs)

        rows.append({
            "N": N,
            "blocks": len(blocks),
            "V_mean": vm,
            "eps": -vm,
            "inv_eps": 1.0 / (-vm) if vm < 0 else float("inf"),
        })

        if N_max >= 1_000_000 and N % 1_000_001 == 1:
            print(f"progress {N}/{N_max}")

    xs = [r["inv_eps"] for r in rows if math.isfinite(r["inv_eps"])]
    ys = [r["blocks"] for r in rows if math.isfinite(r["inv_eps"])]

    a, b = linreg(xs, ys)
    c = corr(xs, ys)

    record = max(rows, key=lambda r: r["blocks"])

    def top_stats(label, subset):
        vals = [r["V_mean"] for r in subset]
        blks = [r["blocks"] for r in subset]
        return {
            "label": label,
            "count": len(subset),
            "mean_V": mean(vals),
            "std_V": std(vals),
            "mean_blocks": mean(blks),
            "max_blocks": max(blks) if blks else 0,
        }

    by_blocks = sorted(rows, key=lambda r: r["blocks"], reverse=True)

    top100 = by_blocks[:100]
    top1000 = by_blocks[:1000]

    top1pct_n = max(1, len(rows) // 100)
    top01pct_n = max(1, len(rows) // 1000)

    top1pct = by_blocks[:top1pct_n]
    top01pct = by_blocks[:top01pct_n]

    return {
        "N_max": N_max,
        "count": len(rows),
        "all_negative": all(r["V_mean"] < 0 for r in rows),
        "a": a,
        "b": b,
        "corr": c,
        "record_N": record["N"],
        "record_blocks": record["blocks"],
        "record_V": record["V_mean"],
        "record_eps": record["eps"],
        "top_stats": [
            top_stats("top100", top100),
            top_stats("top1000", top1000),
            top_stats("top1pct", top1pct),
            top_stats("top0.1pct", top01pct),
        ],
    }


def run():
    scales = [10_000, 100_000, 1_000_000, 10_000_000]
    results = []

    for s in scales:
        print(f"\n=== SCAN N_max={s} ===")
        res = analyze_scale(s)
        results.append(res)

        print(
            f"N_max={res['N_max']} | "
            f"count={res['count']} | "
            f"all_neg={res['all_negative']} | "
            f"a={res['a']:.6f} | "
            f"b={res['b']:.6f} | "
            f"corr={res['corr']:.6f}"
        )
        print(
            f"record N={res['record_N']} | "
            f"blocks={res['record_blocks']} | "
            f"V_mean={res['record_V']:.6f} | "
            f"eps={res['record_eps']:.6f}"
        )

        for t in res["top_stats"]:
            print(
                f"{t['label']:<9} | "
                f"count={t['count']:<7} | "
                f"mean_V={t['mean_V']:.6f} | "
                f"std_V={t['std_V']:.6f} | "
                f"mean_blocks={t['mean_blocks']:.2f} | "
                f"max_blocks={t['max_blocks']}"
            )

    print("\n=== TABLEAU RENORMALISATION ===")
    print("N_max | a | b | corr | record_blocks | record_eps | record_N")
    print("-" * 90)

    for r in results:
        print(
            f"{r['N_max']:<10} | "
            f"{r['a']:<10.6f} | "
            f"{r['b']:<9.6f} | "
            f"{r['corr']:<8.6f} | "
            f"{r['record_blocks']:<13} | "
            f"{r['record_eps']:<10.6f} | "
            f"{r['record_N']}"
        )


if __name__ == "__main__":
    run()
