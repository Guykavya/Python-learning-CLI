## Approach

Fill the 2-D table of chapter section 10, then walk back from `f[n][W]` (chapter section 9, "Method 2: re-derive the choice from the table").

- If `f[i][w] == f[i - 1][w]`, the best for `(i, w)` is already possible without item `i - 1`: leave it out, stay at capacity `w`.
- Otherwise the only way `f[i][w]` got bigger is the "take" option: item `i - 1` is in, and the rest of the bag is the best for `(i - 1, w - wt[i - 1])`.

```python
def pack_van(wt, val, W):
    n = len(wt)
    f = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            f[i][w] = f[i - 1][w]
            if wt[i - 1] <= w:
                f[i][w] = max(f[i][w], f[i - 1][w - wt[i - 1]] + val[i - 1])
    items, w = [], W
    for i in range(n, 0, -1):
        if f[i][w] != f[i - 1][w]:        # the value changed, so item i-1 was taken
            items.append(i - 1)
            w -= wt[i - 1]
    items.reverse()
    return f[n][W], items
```

For the second example, the walk is:

| i | w | `f[i][w]` | `f[i-1][w]` | decision |
|---|---|---|---|---|
| 4 | 10 | 90 | 70 | take item 3 (weight 3), w = 7 |
| 3 | 7 | 40 | 40 | leave item 2 |
| 2 | 7 | 40 | 10 | take item 1 (weight 4), w = 3 |
| 1 | 3 | 0 | 0 | leave item 0 |

Result `(90, [1, 3])`.

## Complexity

`O(n * W)` time and memory for the table; the walk back is `O(n)`. Memory is the price of reconstruction: the one-list version of p036 is `O(W)`, but it keeps only the last row, so the choices are gone.

## Another way

Store the choice while filling (chapter section 9, "Method 1: parent pointers"): a table `took[i][w] = True` when the "take" option won. The walk back reads `took` instead of comparing two cells. It costs a second table, but it is the method that works for every DP, including ones where "the value did not change" does not tell you the choice. To save memory, the choice table can be stored as one big integer bitmask per row.
