import math

data = [
    {"N": 1e4, "a": 11.844116, "eps_record": 0.305800, "top100": 0.393367, "top1000": 0.482870, "top01": 0.316120},
    {"N": 1e5, "a": 15.195203, "eps_record": 0.302447, "top100": 0.340264, "top1000": 0.397793, "top01": 0.329637},
    {"N": 1e6, "a": 18.595370, "eps_record": 0.246078, "top100": 0.299040, "top1000": 0.339319, "top01": 0.324031},
    {"N": 1e7, "a": 21.955995, "eps_record": 0.223554, "top100": 0.263057, "top1000": 0.293712, "top01": 0.327300},
    {"N": 1e8, "a": 25.300466, "eps_record": 0.175627, "top100": 0.238904, "top1000": 0.262576, "top01": 0.333246},
]

def mean(xs):
    return sum(xs) / len(xs)

def linreg(xs, ys):
    mx, my = mean(xs), mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    A = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    B = my - A * mx
    return A, B

def r2(xs, ys, A, B):
    my = mean(ys)
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (A*x + B)) ** 2 for x, y in zip(xs, ys))
    return 1 - ss_res / ss_tot if ss_tot else 0

def power_fit(label, key):
    x = [math.log(d["N"]) for d in data]
    y = [math.log(d[key]) for d in data]

    slope, intercept = linreg(x, y)
    score = r2(x, y, slope, intercept)

    C = math.exp(intercept)
    p = -slope

    print(f"\n=== {label}: eps ~ C * N^-p ===")
    print(f"C={C:.6f} | p={p:.6f} | R²={score:.6f}")

    for d in data:
        pred = C * (d["N"] ** (-p))
        print(
            f"N={d['N']:<10.0f} real={d[key]:.6f} "
            f"pred={pred:.6f} resid={d[key]-pred:+.6f}"
        )

def a_fit():
    x = [math.log(d["N"]) for d in data]
    y = [d["a"] for d in data]

    slope, intercept = linreg(x, y)
    score = r2(x, y, slope, intercept)

    print("=== a(N) ~ alpha ln(N) + beta ===")
    print(f"alpha={slope:.6f} | beta={intercept:.6f} | R²={score:.6f}")

    for d in data:
        pred = slope * math.log(d["N"]) + intercept
        print(
            f"N={d['N']:<10.0f} a={d['a']:.6f} "
            f"pred={pred:.6f} resid={d['a']-pred:+.6f}"
        )

def joint():
    print("\n=== JOINT a * eps ===")
    print("N | a*record | a*top100 | a*top1000 | a*top0.1pct")
    for d in data:
        print(
            f"{d['N']:<10.0f} | "
            f"{d['a']*d['eps_record']:<9.4f} | "
            f"{d['a']*d['top100']:<9.4f} | "
            f"{d['a']*d['top1000']:<9.4f} | "
            f"{d['a']*d['top01']:<9.4f}"
        )

    print("\n=== a / ln(N) ===")
    for d in data:
        print(f"N={d['N']:<10.0f} a/lnN={d['a']/math.log(d['N']):.6f}")

if __name__ == "__main__":
    a_fit()
    power_fit("record", "eps_record")
    power_fit("top100", "top100")
    power_fit("top1000", "top1000")
    power_fit("top0.1pct", "top01")
    joint()
