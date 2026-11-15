n = int(input())


def ask(i):
    print("?", i, flush=True)
    return int(input())


lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if ask(mid) < ask(mid + 1):
        lo = mid + 1
    else:
        hi = mid
print("!", lo, flush=True)
