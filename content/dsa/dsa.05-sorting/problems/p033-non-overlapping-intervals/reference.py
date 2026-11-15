n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
intervals.sort(key=lambda x: x[1])
kept = 0
last_end = -10**18
for l, r in intervals:
    if l >= last_end:
        kept += 1
        last_end = r
print(n - kept)
