n, k = map(int, input().split())
a = [int(x) for x in input().split()]
count = [0] * (k + 1)
for x in a:
    count[x] += 1
out = []
for v in range(k + 1):
    out.extend([v] * count[v])
print(" ".join(map(str, out)))
