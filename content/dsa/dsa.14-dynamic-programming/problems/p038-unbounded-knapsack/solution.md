## Approach

Chapter section 11. `g[w]` = the best value for capacity `w`, any number of copies of each item.

- **Transition:** `g[w] = max(g[w], g[w - wt[i]] + val[i])` for every item that fits. Because `g[w - wt[i]]` may already contain copies of item `i`, adding one more is allowed: that is exactly "unlimited".
- **Base:** `g[w] = 0` for every `w` to start with (an empty bag is always allowed, so leftover space costs nothing).
- **Order:** the capacity loop goes **upwards**, so `g[w - wt[i]]` is already updated for item `i`.

```python
def unbounded_knapsack(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(wt[i], W + 1):            # upwards: the item may repeat
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]
```

For `[2, 3]`, `[10, 14]`, `W = 7`:

| w | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| after item 0 (2, 10) | 0 | 0 | 10 | 10 | 20 | 20 | 30 | 30 |
| after item 1 (3, 14) | 0 | 0 | 10 | 14 | 20 | 24 | 30 | 34 |

`g[7] = g[4] + 14 = 34`: two 2s and one 3.

The pair to remember, from chapter section 11:

| Items | Capacity loop | Why |
|---|---|---|
| each at most once (p036) | high to low | `g[w - wt]` must be the old value |
| unlimited (this problem) | low to high | `g[w - wt]` may already include this item |

## Complexity

`O(len(wt) * W)` time, `O(W)` memory.

## Another way

Capacity outside, items inside: `for w in 1..W: for each item that fits: g[w] = max(g[w], g[w - wt[i]] + val[i])`. For a **maximum** both loop orders give the same answer, because the order in which items are put into the bag does not change its value. (For **counting**, p018 and p020 showed that the two orders count different things.)
