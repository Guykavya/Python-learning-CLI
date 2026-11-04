n, k = map(int, input().split())
a = [int(x) for x in input().split()]

s = sum(a[:k])
best = s
for r in range(k, n):
    s += a[r] - a[r - k]
    if s > best:
        best = s

print(best)
