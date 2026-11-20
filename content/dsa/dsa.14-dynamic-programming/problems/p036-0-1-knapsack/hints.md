## Hint 1

Think about the last item considered, item `i - 1`. Either it stays out, and the best is `f[i - 1][w]`; or it goes in (only if `wt[i - 1] <= w`), and the best is `f[i - 1][w - wt[i - 1]] + val[i - 1]`. Take the larger. Row 0 (no items) is all zeros.

## Hint 2

```
f = (n + 1) rows of (W + 1) zeros
for i in 1..n:
    for w in 0..W:
        f[i][w] = f[i-1][w]
        if wt[i-1] <= w:
            f[i][w] = max(f[i][w], f[i-1][w - wt[i-1]] + val[i-1])
```

## Hint 3

For one list `g`: row `i` reads only row `i - 1`, so overwrite `g` in place. Going **downwards** (`w` from `W` to `wt[i]`), the smaller cell `g[w - wt[i]]` is visited later, so when you read it, it still holds the old row's value.

```
g = [0] * (W + 1)
for each item i:
    for w from W down to wt[i]:
        g[w] = max(g[w], g[w - wt[i]] + val[i])
return g[W]
```
