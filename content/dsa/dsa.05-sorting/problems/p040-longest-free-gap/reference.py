t, n = map(int, input().split())
meetings = []
for _ in range(n):
    l, r = map(int, input().split())
    meetings.append((l, r))
meetings.sort()
busy_until = 0
best = 0
for l, r in meetings:
    best = max(best, l - busy_until)
    busy_until = max(busy_until, r)
best = max(best, t - busy_until)
print(best)
