n, m = map(int, input().split())
a = [int(x) for x in input().split()]


def pieces(limit):
    count, cur = 1, 0
    for x in a:
        if cur + x > limit:
            count += 1
            cur = 0
        cur += x
    return count


lo, hi = max(a), sum(a)
while lo < hi:
    mid = (lo + hi) // 2
    if pieces(mid) <= m:
        hi = mid
    else:
        lo = mid + 1
print(lo)
