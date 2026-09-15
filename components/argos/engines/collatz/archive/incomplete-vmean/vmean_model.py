# collatz_scanner/src/vmean_model.py

import math
from trajectory import extract_blocks


LOG2_3 = math.log2(3)


def compute_Vj(b):
    L = b["L_j"]
    k = b["k_rupture"]
    return (L + 1) * LOG2_3 - (L + k)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def variance(xs):
    if not xs:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def corr(xs, ys):
    if len(xs) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (denx * deny) if denx and deny else 0.0


def linreg(xs, ys):
    """
    y = a*x + b
    """
    mx = mean(xs)
    my = mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return 0.0, my
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    b = my - a * mx
    return a, b


def collect(N_max=10000):
    rows = []

    for N in range(1, N_max + 1, 2):
        blocks = extract_blocks(N)
        if len(blocks) < 3:
            continue

        Vs = [compute_Vj(b) for b in blocks]
        V_mean = mean(Vs)

        rows.append({
            "N": N,
            "blocks": len(blocks),
            "V_mean": V_mean,
            "inv_neg_V": 1.0 / (-V_mean) if V_mean < 0 else float("inf"),
        })

    return rows


def deciles(rows):
    rows = sorted(rows, key=lambda r: r["V_mean"])
    n = len(rows)
    size = n // 10

    print("\n=== DÉCILES V_MEAN -> DURÉE ===")
    print("decile | V_mean | avg_blocks | min | max | count")
    print("-" * 70)

    for i in range(10):
        lo = i * size
        hi = n if i == 9 else (i + 1) * size
        chunk = rows[lo:hi]

        print(
            f"{i:<6} | "
            f"{mean([r['V_mean'] for r in chunk]):<8.4f} | "
            f"{mean([r['blocks'] for r in chunk]):<10.2f} | "
            f"{min(r['blocks'] for r in chunk):<3} | "
            f"{max(r['blocks'] for r in chunk):<3} | "
            f"{len(chunk)}"
        )


def model(rows):
    xs = [r["inv_neg_V"] for r in rows if math.isfinite(r["inv_neg_V"])]
    ys = [r["blocks"] for r in rows if math.isfinite(r["inv_neg_V"])]

    a, b = linreg(xs, ys)
    c = corr(xs, ys)

    print("\n=== MODÈLE blocks ≈ a / (-V_mean) + b ===")
    print(f"a = {a:.4f}")
    print(f"b = {b:.4f}")
    print(f"corr(1/-V_mean, blocks) = {c:.4f}")


def critical_thresholds(rows):
    print("\n=== SEUILS EMPIRIQUES ===")
    for threshold in (-0.70, -0.60, -0.55, -0.50, -0.45, -0.40, -0.35):
        sub = [r for r in rows if r["V_mean"] >= threshold]
        if not sub:
            continue

        print(
            f"V_mean >= {threshold:<5} | "
            f"count={len(sub):<5} | "
            f"avg_blocks={mean([r['blocks'] for r in sub]):<7.2f} | "
            f"min={min(r['blocks'] for r in sub):<3} | "
            f"max={max(r['blocks'] for r in sub):<3}"
        )


def universality(rows):
    print("\n=== CONVERGENCE / BANDE DES PLUS LONGUES ===")

    for cutoff in (20, 25, 30, 35, 40):
        sub = [r for r in rows if r["blocks"] >= cutoff]
        if not sub:
            continue

        vals = [r["V_mean"] for r in sub]
        print(
            f"blocks >= {cutoff:<2} | "
            f"count={len(sub):<5} | "
            f"mean_V={mean(vals):<8.5f} | "
            f"std_V={math.sqrt(variance(vals)):<8.5f} | "
            f"min_V={min(vals):<8.5f} | "
            f"max_V={max(vals):<8.5f}"
        )


def top(rows):
    print("\n=== TOP 25 V_MEAN LES MOINS NÉGATIFS ===")
    for r in sorted(rows, key=lambda x: x["V_mean"], reverse=True)[:25]:
        print(f"N={r['N']:<5} | blocks={r['blocks']:<3} | V_mean={r['V_mean']:.6f}")


def run(N_max=10000):
    rows = collect(N_max=N_max)

    print("=== V_MEAN MODEL ===")
    print(f"N_max={N_max}")
    print(f"trajectoires={len(rows)}")

    vmax = max(rows, key=lambda r: r["V_mean"])
    vmin = min(rows, key=lambda r: r["V_mean"])

    print(f"max V_mean = {vmax['V_mean']:.6f} | N={vmax['N']} | blocks={vmax['blocks']}")
    print(f"min V_mean = {vmin['V_mean']:.6f} | N={vmin['N']} | blocks={vmin['blocks']}")
    print(f"all V_mean < 0 ? {all(r['V_mean'] < 0 for r in rows)}")

    deciles(rows)
    model(rows)
    critical_thresholds(rows)
    universality(rows)
    top(rows)


if __name__ == "__main__":
    run(N_max=10000)
