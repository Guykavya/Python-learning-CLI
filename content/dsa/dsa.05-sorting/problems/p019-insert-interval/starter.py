n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
a, b = map(int, input().split())
# TODO: insert [a, b] and merge overlapping or touching intervals
for l, r in intervals:
    print(l, r)
