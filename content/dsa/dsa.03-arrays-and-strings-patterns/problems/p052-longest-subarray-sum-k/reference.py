n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

first = {0: 0}      # prefix value -> the first index where it appeared (P[0] = 0 at index 0)
best = 0
pre = 0
for i in range(1, n + 1):
    pre += a[i - 1]                # pre = P[i]
    j = first.get(pre - k)
    if j is not None and i - j > best:
        best = i - j
    if pre not in first:           # keep the earliest index: it gives the longest subarray later
        first[pre] = i
print(best)
