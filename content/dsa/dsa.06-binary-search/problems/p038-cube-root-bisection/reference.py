t = int(input())
for _ in range(t):
    c = int(input())
    lo, hi = 0.0, 100000.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if mid * mid * mid + mid >= c:
            hi = mid
        else:
            lo = mid
    print(f"{(lo + hi) / 2:.6f}")
