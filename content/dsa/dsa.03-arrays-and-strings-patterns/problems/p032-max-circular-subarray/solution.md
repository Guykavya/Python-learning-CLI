## Approach

Split by shape:

1. **No wrap**: an ordinary subarray. Kadane gives the best one, `best_max`.
2. **Wrap**: the subarray is a prefix plus a suffix. What it leaves out is one ordinary subarray in the middle.
   So its sum is `total - middle`, and the best wrap removes the **smallest** middle: `total - best_min`, where
   `best_min` comes from Kadane with `min`.

The answer is the larger of the two, with one trap. If every number is negative, `best_min` is the whole array and
`total - best_min = 0`: that is the sum of **nothing**, which is not allowed. In that case (`best_max < 0`) the
answer is `best_max`, the largest single element.

## Code

```python
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
```

Example `5 -3 -4 2 5`: `best_max = 7` (`2 5`), `best_min = -7` (`-3 -4`), `total = 5`. The wrap gives
`5 - (-7) = 12`, better than 7.

## Complexity

O(n) time, one pass for both Kadanes plus `sum`. O(1) extra memory.

## Another way

Double the array (`a + a`) and look for the best subarray of length at most `n` in it. With prefix sums `P`, that is
`max(P[j] - P[i])` over `j - n <= i < j`; keep the smallest `P[i]` of the last `n` positions in a monotonic deque.
Also O(n), but harder to write. Plain Kadane on `a + a` is wrong: it can take more than `n` elements.
