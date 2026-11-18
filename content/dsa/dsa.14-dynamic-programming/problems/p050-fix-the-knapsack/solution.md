## The bug

The inner loop goes **upwards**. When `best[c]` reads `best[c - w]`, that smaller cell was already visited in this pass and may already contain parcel `i`. So a parcel can be taken again and again: the starter solves the **unbounded** knapsack (chapter section 11), not the 0/1 knapsack.

Trace of the starter for `knapsack([2], [10], 7)`:

| c | reads | best[c] |
|---|---|---|
| 2 | best[0] = 0 | 10 |
| 3 | best[1] = 0 | 10 |
| 4 | best[2] = **10** (already this parcel) | 20 |
| 6 | best[4] = 20 | 30 |
| 7 | best[5] = 20 | 30 |

Why does `[1, 3, 4, 5], [1, 4, 5, 7], 7` still give 9? There, using a parcel twice never beats the best real choice (two copies of `(3, 4)` give 8, one `(1, 1)` plus two `(3, 4)` give 9, the same as the true answer). A bug can hide on friendly inputs; that is why the tests compare with brute force on many random inputs.

## The fix

```python
def knapsack(weights, values, capacity):
    """0/1 knapsack: each parcel at most once. Return the best total value."""
    best = [0] * (capacity + 1)
    for i in range(len(weights)):
        for c in range(capacity, weights[i] - 1, -1):     # downwards: best[c - w] is still old
            best[c] = max(best[c], best[c - weights[i]] + values[i])
    return best[capacity]
```

Going downwards, `c - w < c` is visited **after** `c`, so it still holds the value from before parcel `i`: exactly the 2-D table's `f[i-1][c - w]`.

## Complexity

`O(n * capacity)` time, `O(capacity)` space, unchanged.

## Another way

Keep two arrays: `new = best[:]`, then `new[c] = max(best[c], best[c - w] + v)` in any order, and `best = new`. It is also correct (every read is from the old array) and does not depend on the loop direction, at the cost of one copy per parcel. The 2-D table of chapter section 10 is the clearest of all, but the task asks for one array.
