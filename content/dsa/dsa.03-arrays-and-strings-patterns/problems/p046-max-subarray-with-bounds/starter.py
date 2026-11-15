n = int(input())
a = [int(x) for x in input().split()]

best_sum, best_l, best_r = a[0], 1, 1
# TODO: Kadane with a current run (cur, cur_start); decide carefully when to restart and when to replace the best.
print(best_sum, best_l, best_r)
