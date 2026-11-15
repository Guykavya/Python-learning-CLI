n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
# TODO: sort by start, then merge overlapping or touching intervals
for l, r in intervals:
    print(l, r)
