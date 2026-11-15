n, m, k = map(int, input().split())


def A(i):
    print("? A", i, flush=True)
    return int(input())


def B(j):
    print("? B", j, flush=True)
    return int(input())


lo, hi = max(0, k - m), min(k, n)
while lo < hi:
    i = (lo + hi) // 2
    j = k - i
    if A(i) < B(j - 1):
        lo = i + 1
    else:
        hi = i
i = lo
j = k - i
best = []
if i > 0:
    best.append(A(i - 1))
if j > 0:
    best.append(B(j - 1))
print("!", max(best), flush=True)
