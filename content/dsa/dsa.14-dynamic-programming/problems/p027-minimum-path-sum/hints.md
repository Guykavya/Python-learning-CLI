## Hint 1

The last step into `(r, c)` came from above or from the left. The cheapest path to `(r, c)` is the cheaper of the two best paths to those cells, plus `grid[r][c]`. What are the special cases where one (or both) of those neighbours does not exist?

## Hint 2

Four cases: the start (`f = grid[0][0]`); the first row (only from the left); the first column (only from above); everything else (`grid[r][c] + min(above, left)`). Fill row by row, left to right, and return the bottom-right value.

## Hint 3

```
for r in 0..rows-1:
    for c in 0..cols-1:
        if r == 0 and c == 0: f[r][c] = grid[0][0]
        elif r == 0:         f[r][c] = f[r][c-1] + grid[r][c]
        elif c == 0:         f[r][c] = f[r-1][c] + grid[r][c]
        else:                f[r][c] = grid[r][c] + min(f[r-1][c], f[r][c-1])
return f[rows-1][cols-1]
```
