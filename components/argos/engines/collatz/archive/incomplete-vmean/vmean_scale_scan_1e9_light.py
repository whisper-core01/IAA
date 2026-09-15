# collatz_scanner/src/vmean_scale_scan_1e9_light.py

import math
import heapq
from trajectory import extract_blocks

LOG2_3 = math.log2(3)
N_MAX = 1_000_000_000
TOP_K = 10_000


def V(b):
    return (b["L_j"] + 1) * LOG2_3 - (b["L_j"] + b["k_rupture"])


class OnlineLinReg:
    def __init__(self):
        self.n = 0
        self.sx = 0.0
        self.sy = 0.0
        self.sxx = 0.0
        self.syy = 0.0
        self.sxy = 0.0

    def add(self, x, y):
        self.n += 1
        self.sx += x
        self.sy += y
        self.sxx += x * x
        self.syy += y * y
        self.sxy += x * y

    def fit(self):
        n = self.n
        den = n * self.sxx - self.sx * self.sx
        if den == 0:
            return 0.0, 0.0, 0.0

        a = (n * self.sxy - self.sx * self.sy) / den
        b = (self.sy - a * self.sx) / n

        corr_den = math.sqrt(
            (n * self.sxx - self.sx * self.sx) *
            (n * self.syy - self.sy * self.sy)
        )
        corr = (n * self.sxy - self.sx * self.sy) / corr_den if corr_den else 0.0

        return a, b, corr


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if not xs:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def top_stats(label, heap, k):
    top = sorted(heap, key=lambda x: x[0], reverse=True)[:k]
    vals = [item[2] for item in top]
    blocks = [item[0] for item in top]

    return {
        "label": label,
        "count": len(top),
        "mean_V": mean(vals),
        "std_V": std(vals),
        "mean_blocks": mean(blocks),
        "max_blocks": max(blocks) if blocks else 0,
    }


def scan():
    reg = OnlineLinReg()
    top_heap = []

    count = 0
    all_negative = True
    record = None

    for N in range(1, N_MAX + 1, 2):
        blocks = extract_blocks(N)
        if len(blocks) < 3:
            continue

        vs = [V(b) for b in blocks]
        vm = mean(vs)

        if vm >= 0:
            all_negative = False

        inv_eps = 1.0 / (-vm)
        block_count = len(blocks)

        reg.add(inv_eps, block_count)
        count += 1

        item = (block_count, N, vm)

        if record is None or block_count > record[0]:
            record = item

        if len(top_heap) < TOP_K:
            heapq.heappush(top_heap, item)
        else:
            if block_count > top_heap[0][0]:
                heapq.heapreplace(top_heap, item)

        if N % 50_000_001 == 1:
            print(f"progress {N}/{N_MAX}", flush=True)

    a, b, corr = reg.fit()

    print("\n=== RESULTAT 1E9 LIGHT ===")
    print(
        f"N_max={N_MAX} | "
        f"count={count} | "
        f"all_neg={all_negative} | "
        f"a={a:.6f} | "
        f"b={b:.6f} | "
        f"corr={corr:.6f}"
    )

    print(
        f"record N={record[1]} | "
        f"blocks={record[0]} | "
        f"V_mean={record[2]:.6f} | "
        f"eps={-record[2]:.6f}"
    )

    print("\n=== TOP STATS ===")
    for label, k in (
        ("top100", 100),
        ("top1000", 1000),
        ("top10000", 10000),
    ):
        t = top_stats(label, top_heap, k)
        print(
            f"{t['label']:<10} | "
            f"count={t['count']:<8} | "
            f"mean_V={t['mean_V']:.6f} | "
            f"std_V={t['std_V']:.6f} | "
            f"mean_blocks={t['mean_blocks']:.2f} | "
            f"max_blocks={t['max_blocks']}"
        )

    print("\n=== RENORM PRODUCTS ===")
    for label, k in (
        ("top100", 100),
        ("top1000", 1000),
        ("top10000", 10000),
    ):
        t = top_stats(label, top_heap, k)
        eps = -t["mean_V"]
        print(f"{label:<10} | a*eps={a * eps:.6f}")

    print(f"record    | a*eps={a * (-record[2]):.6f}")


if __name__ == "__main__":
    scan()
