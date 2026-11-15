t = int(input())


def ask(i):
    print("?", i, flush=True)
    return int(input())


hi = 1
while ask(hi) < t:
    hi *= 2
lo = hi // 2
ans = -1
while lo <= hi:
    mid = (lo + hi) // 2
    v = ask(mid)
    if v == t:
        ans = mid
        break
    elif v < t:
        lo = mid + 1
    else:
        hi = mid - 1
print("!", ans, flush=True)
