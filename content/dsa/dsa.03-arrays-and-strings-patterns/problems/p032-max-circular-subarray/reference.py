n = int(input())
a = [int(x) for x in input().split()]

# Kadane twice in one pass: the best (largest) and the worst (smallest) non-empty subarray.
cur_max = best_max = a[0]
cur_min = best_min = a[0]
for x in a[1:]:
    cur_max = max(x, cur_max + x)
    best_max = max(best_max, cur_max)
    cur_min = min(x, cur_min + x)
    best_min = min(best_min, cur_min)

total = sum(a)
if best_max < 0:
    print(best_max)                 # all negative: the wrap would take nothing at all
else:
    print(max(best_max, total - best_min))
