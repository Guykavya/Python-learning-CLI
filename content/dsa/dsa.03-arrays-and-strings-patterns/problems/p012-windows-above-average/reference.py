n, k, t = map(int, input().split())
a = [int(x) for x in input().split()]

need = t * k
s = sum(a[:k])
count = 1 if s >= need else 0
for r in range(k, n):
    s += a[r] - a[r - k]
    if s >= need:
        count += 1

print(count)
