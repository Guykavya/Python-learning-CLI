n, k = map(int, input().split())
a = [int(x) for x in input().split()]

seen = {}          # prefix sum -> index where it was reached
total = 0
best = 0
for i, x in enumerate(a):
    total += x
    seen[total] = i
    if total + k in seen:
        best = max(best, i - seen[total + k])
print(best)
