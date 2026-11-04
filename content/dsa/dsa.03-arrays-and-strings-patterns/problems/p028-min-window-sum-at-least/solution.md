## Approach

A variable-size window. Move `r` right and add `a[r]`. As soon as the sum is `>= s`, the window is a candidate;
then shrink it from the left as long as it stays `>= s`, recording each length. When it drops below `s`, grow
again.

Why no window is missed: for each `r`, the inner loop moves `l` to the first position where the window would
fail. With positive numbers, any window ending at `r` that starts further left is longer, and any that starts
further right has a smaller sum. So the shortest good window ending at `r` is the last one recorded.

## Code

```python
n, s = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

best = n + 1                 # "no window found yet": longer than any real window
total = 0
l = 0
for r in range(n):
    total += a[r]
    while total >= s:        # the window a[l..r] is good: record it, then try to shrink it
        if r - l + 1 < best:
            best = r - l + 1
        total -= a[l]
        l += 1

print(best if best <= n else 0)
```

On the example (`s = 7`):

| r | a[r] | total after adding | recorded lengths | window left |
|---|---|---|---|---|
| 0 | 2 | 2 | | 2 |
| 1 | 3 | 5 | | 2 3 |
| 2 | 1 | 6 | | 2 3 1 |
| 3 | 2 | 8 | 4 (2 3 1 2) | 3 1 2 (sum 6) |
| 4 | 4 | 10 | 4 (3 1 2 4), 3 (1 2 4) | 2 4 (sum 6) |
| 5 | 3 | 9 | 3 (2 4 3), 2 (4 3) | 3 (sum 3) |

## Complexity

O(n): `r` moves `n` times, and `l` moves at most `n` times over the whole run. O(1) extra memory.

## Another way

Prefix sums `P` are strictly increasing because the numbers are positive. For every `r`, binary search the
largest `l` with `P[r+1] - P[l] >= s` (`bisect_right(P, P[r+1] - s) - 1`). That is O(n log n). Both methods need
positive numbers; with negative numbers, use prefix sums and a monotonic deque instead.
