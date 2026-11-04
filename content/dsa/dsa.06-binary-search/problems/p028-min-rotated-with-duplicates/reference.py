t = int(input())
for _ in range(t):
    n = int(input())
    a = [int(x) for x in input().split()]
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        elif a[mid] < a[hi]:
            hi = mid
        else:
            hi -= 1
    print(a[lo])
