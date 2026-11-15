n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
queries = [int(x) for x in input().split()]


def lower(x):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper(x):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


print("\n".join(str(upper(x) - lower(x)) for x in queries))
