n, c = map(int, input().split())
stalls = sorted(int(x) for x in input().split())


def can_place(d):
    placed, last = 1, stalls[0]
    for s in stalls:
        if s - last >= d:
            placed += 1
            last = s
    return placed >= c


lo, hi = 1, (stalls[-1] - stalls[0]) // (c - 1)
while lo < hi:
    mid = (lo + hi + 1) // 2
    if can_place(mid):
        lo = mid
    else:
        hi = mid - 1
print(lo)
