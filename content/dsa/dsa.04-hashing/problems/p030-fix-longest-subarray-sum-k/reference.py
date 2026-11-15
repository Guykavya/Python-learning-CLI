n, k = map(int, input().split())
a = [int(x) for x in input().split()]

seen = {0: -1}
total = 0
best = 0
for i, x in enumerate(a):
    total += x
    if total - k in seen:
        best = max(best, i - seen[total - k])
    if total not in seen:
        seen[total] = i
print(best)
