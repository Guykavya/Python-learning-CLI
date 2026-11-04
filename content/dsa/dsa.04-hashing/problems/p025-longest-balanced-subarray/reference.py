n = int(input())
a = [int(x) for x in input().split()]

first = {0: -1}
s = 0
best = 0
for i, x in enumerate(a):
    s += 1 if x == 1 else -1
    if s in first:
        best = max(best, i - first[s])
    else:
        first[s] = i
print(best)
