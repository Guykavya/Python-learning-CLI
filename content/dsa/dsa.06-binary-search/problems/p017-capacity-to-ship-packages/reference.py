n, d = map(int, input().split())
w = [int(x) for x in input().split()]


def days_needed(cap):
    days, load = 1, 0
    for x in w:
        if load + x > cap:
            days += 1
            load = 0
        load += x
    return days


lo, hi = max(w), sum(w)
while lo < hi:
    mid = (lo + hi) // 2
    if days_needed(mid) <= d:
        hi = mid
    else:
        lo = mid + 1
print(lo)
