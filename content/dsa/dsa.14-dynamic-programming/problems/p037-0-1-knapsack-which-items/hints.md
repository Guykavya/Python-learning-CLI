## Hint 1

Build the full table `f[i][w]` of p036 (the one-list version overwrites the rows you need to walk back through). Then start at `i = n`, `w = W` and go up one row at a time.

## Hint 2

At row `i`, compare `f[i][w]` with the cell straight above, `f[i - 1][w]`. If they are equal, the best value for `(i, w)` was reachable **without** item `i - 1`, so leave it out and keep `w`. If they differ, item `i - 1` must have been taken: record it and subtract its weight from `w`.

## Hint 3

```
f = knapsack table
items = []; w = W
for i from n down to 1:
    if f[i][w] != f[i-1][w]:
        items.append(i - 1)
        w -= wt[i - 1]
items.reverse()
return f[n][W], items
```
