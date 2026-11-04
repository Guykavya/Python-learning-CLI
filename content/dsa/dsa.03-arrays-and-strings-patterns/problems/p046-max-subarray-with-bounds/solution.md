## Approach

Kadane with positions. At each `i`, `cur` is the largest sum of a subarray **ending at `i`**, and `cur_start` is the
earliest start that achieves it. Two decisions, two halves of the tie rule:

- **Restart or extend?** The best run ending at `i` either extends the run ending at `i - 1` (sum `cur + a[i]`) or is
  just `a[i]`. They are equal when `cur == 0`; extending keeps the earlier start. So restart only when `cur < 0`.
- **Replace the best?** Only when `cur > best`. Why is that enough for "earliest start, then shortest"? Each
  restart happens at a new, strictly smaller prefix sum, so `cur_start` never moves backwards as `i` grows. The first
  `i` that reaches the maximum therefore has the smallest start, and for that start it is the smallest end.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

cur, cur_start = a[0], 0
best_sum, best_l, best_r = a[0], 0, 0
for i in range(1, n):
    if cur >= 0:
        cur += a[i]
    else:
        cur, cur_start = a[i], i
    if cur > best_sum:
        best_sum, best_l, best_r = cur, cur_start, i

print(best_sum, best_l + 1, best_r + 1)
```

Walk through `-1 0 2`: `i = 0`: cur -1. `i = 1`: cur < 0, restart: cur 0, start 1; 0 > -1, best (0, 1, 1).
`i = 2`: cur = 0 is not negative, extend: cur 2, start still 1; best (2, 1, 2). Printed 1-based: `2 2 3`.

## Complexity

O(n) time, O(1) extra memory.

## Another way

Prefix sums: the subarray `a[l..r]` has sum `P[r + 1] - P[l]`. For a fixed end, the best start is the position of the
**smallest** prefix sum before it; with ties, its **first** position. Keep the running minimum and where it first
appeared, and compare candidates as tuples `(sum, -l, -r)`, so that Python's tuple comparison applies the tie rule for
you. This is exactly what Kadane does, written with prefix sums.
