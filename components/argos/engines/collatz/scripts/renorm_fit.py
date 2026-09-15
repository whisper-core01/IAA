import math

N = [1e4, 1e5, 1e6, 1e7, 1e8]
a = [11.844116, 15.195203, 18.595370, 21.955995, 25.300466]
b = [0.309812, 0.240853, 0.145549, 0.097607, 0.069823]

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
    return 1 - ss_res / ss_tot

logN = [math.log(x) for x in N]

slope, intercept = linreg(logN, a)
score = r2(logN, a, slope, intercept)

print("=== FIT a(Nmax) = alpha * ln(Nmax) + beta ===")
print(f"alpha = {slope:.6f}")
print(f"beta  = {intercept:.6f}")
print(f"R²    = {score:.6f}")

print("\nNmax | a_real | a_pred | residu")
for n, x, real in zip(N, logN, a):
    pred = slope * x + intercept
    print(f"{n:<10.0f} | {real:<9.6f} | {pred:<9.6f} | {real - pred:+.6f}")

print("\n=== TEST b ~ gamma / ln(Nmax) ===")
gammas = [bb * x for bb, x in zip(b, logN)]
gamma = mean(gammas)

print(f"gamma moyen = {gamma:.6f}")

print("\nNmax | b_real | b_pred | residu | b*lnN")
for n, x, real in zip(N, logN, b):
    pred = gamma / x
    print(f"{n:<10.0f} | {real:<8.6f} | {pred:<8.6f} | {real - pred:+.6f} | {real*x:.6f}")
