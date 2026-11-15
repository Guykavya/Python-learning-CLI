n, m, k = map(int, input().split())
bloom = [int(x) for x in input().split()]


def bouquets(day):
    run = count = 0
    for b in bloom:
        if b <= day:
            run += 1
            if run == k:
                count += 1
                run = 0
        else:
            run = 0
    return count


if m * k > n:
    print(-1)
else:
    lo, hi = min(bloom), max(bloom)
    while lo < hi:
        mid = (lo + hi) // 2
        if bouquets(mid) >= m:
            hi = mid
        else:
            lo = mid + 1
    print(lo)
