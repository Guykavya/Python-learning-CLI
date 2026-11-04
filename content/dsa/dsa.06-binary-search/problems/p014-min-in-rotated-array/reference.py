n = int(input())


def ask(i):
    print("?", i, flush=True)
    return int(input())


lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if ask(mid) > ask(hi):
        lo = mid + 1
    else:
        hi = mid
print("!", ask(lo), flush=True)
