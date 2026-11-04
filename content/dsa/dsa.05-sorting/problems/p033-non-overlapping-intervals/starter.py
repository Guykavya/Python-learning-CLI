n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
# TODO: fewest intervals to remove so that the rest do not overlap (touching is fine)
print(0)
