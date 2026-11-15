n, k = map(int, input().split())
a = [int(x) for x in input().split()]

count = {}
for x in a:
    count[x] = count.get(x, 0) + 1

ranked = sorted(count, key=lambda v: (-count[v], v))
print(*ranked[:k])
