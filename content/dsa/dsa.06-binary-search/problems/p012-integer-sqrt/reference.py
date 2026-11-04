q = int(input())
for _ in range(q):
    n = int(input())
    lo, hi = 0, n + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid > n:
            hi = mid
        else:
            lo = mid + 1
    print(lo - 1)
