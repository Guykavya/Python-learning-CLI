n = int(input())
a = [int(x) for x in input().split()]

cur, cur_start = a[0], 0
best_sum, best_l, best_r = a[0], 0, 0
for i in range(1, n):
    if cur >= 0:
        # extending a run with sum 0 keeps the earlier start: same sum, smaller l
        cur += a[i]
    else:
        cur, cur_start = a[i], i
    if cur > best_sum:
        # strict: an equal sum found later has a later end (and a start that is not earlier)
        best_sum, best_l, best_r = cur, cur_start, i

print(best_sum, best_l + 1, best_r + 1)
