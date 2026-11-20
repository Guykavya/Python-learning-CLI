## Approach

Chapter section 10.

- **State:** `f[i][w]` = the best value using only the first `i` items with capacity `w`.
- **Transition:** leave item `i - 1` (`f[i - 1][w]`) or, if it fits, take it (`f[i - 1][w - wt[i - 1]] + val[i - 1]`); keep the larger.
- **Base:** row 0 is all zeros (no items, no value); column 0 is all zeros (no capacity).
- **Answer:** `f[n][W]`.

```python
def knapsack_table(wt, val, W):
    n = len(wt)
    f = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            f[i][w] = f[i - 1][w]                                   # leave item i-1
            if wt[i - 1] <= w:
                f[i][w] = max(f[i][w], f[i - 1][w - wt[i - 1]] + val[i - 1])   # take it
    return f


def knapsack(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):          # downwards: each item once
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]
```

Row `i` of the table reads only row `i - 1`. So `knapsack` keeps one list and overwrites it, item by item. The `take` option must read the **old** value of `g[w - wt[i]]` (the row above). Going from high `w` to low `w`, the smaller index is visited later, so it is still old when it is read. That is the whole reason for the downward loop.

## Complexity

`O(n * W)` time for both. `knapsack_table` uses `O(n * W)` memory; `knapsack` uses `O(W)`. The time depends on the **number** `W`, not on its number of digits: knapsack is "pseudo-polynomial", and with `W = 10**12` neither version is possible.

## Another way

Top-down: `best(i, w) = max(best(i + 1, w), val[i] + best(i + 1, w - wt[i]) if it fits)` with `functools.cache`. It touches only the states that are reachable, which can be far fewer than `n * W` when the weights are large. But the recursion is `n` levels deep and the memo is a dictionary, so for 200 items and `W = 10**4` the table is faster and simpler. The tests' brute force tries all `2**n` subsets, which is only possible for small `n`.
