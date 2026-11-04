n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
a, b = map(int, input().split())
out = []
i = 0
while i < n and intervals[i][1] < a:
    out.append(intervals[i])
    i += 1
while i < n and intervals[i][0] <= b:
    a = min(a, intervals[i][0])
    b = max(b, intervals[i][1])
    i += 1
out.append((a, b))
while i < n:
    out.append(intervals[i])
    i += 1
for l, r in out:
    print(l, r)
