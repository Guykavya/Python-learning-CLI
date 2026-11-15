n = int(input())
a = [int(x) for x in input().split()]

cur = best = a[0]
for x in a[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)

print(best)
