n, t = map(int, input().split())
k = [int(x) for x in input().split()]
lo, hi = 1, min(k) * t
while lo < hi:
    mid = (lo + hi) // 2
    if sum(mid // x for x in k) >= t:
        hi = mid
    else:
        lo = mid + 1
print(lo)
