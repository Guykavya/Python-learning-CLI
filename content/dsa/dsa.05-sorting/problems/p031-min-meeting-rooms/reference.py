n = int(input())
starts = []
ends = []
for _ in range(n):
    s, e = map(int, input().split())
    starts.append(s)
    ends.append(e)
starts.sort()
ends.sort()
j = 0
best = 0
for i, s in enumerate(starts):
    while ends[j] <= s:
        j += 1
    best = max(best, i + 1 - j)
print(best)
