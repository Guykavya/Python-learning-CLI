B = 911382323
M = (1 << 61) - 1

s = input().strip()
n = len(s)
vals = [ord(c) - 96 for c in s]


def repeats(k):
    h = 0
    for i in range(k):
        h = (h * B + vals[i]) % M
    top = pow(B, k - 1, M)
    seen = {h}
    for i in range(k, n):
        h = ((h - vals[i - k] * top) * B + vals[i]) % M
        if h in seen:
            return True
        seen.add(h)
    return False


lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi + 1) // 2
    if repeats(mid):
        lo = mid
    else:
        hi = mid - 1
print(lo)
