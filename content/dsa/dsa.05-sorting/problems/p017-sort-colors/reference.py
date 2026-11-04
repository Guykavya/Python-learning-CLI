n = int(input())
a = [int(x) for x in input().split()]
count = [0, 0, 0]
for x in a:
    count[x] += 1
out = []
for v in range(3):
    out.extend([v] * count[v])
print(" ".join(map(str, out)))
