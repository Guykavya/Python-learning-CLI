## Hint 1

Same recipe as unique paths: `f[r][c]` = the number of paths to `(r, c)`, and `f[r][c] = f[r-1][c] + f[r][c-1]`. One new rule: if `grid[r][c] == 1`, then `f[r][c] = 0`. Why does a 0 here also remove every path that would have passed through the obstacle?

## Hint 2

Do **not** pre-fill the first row and column with 1s: an obstacle in the first row must cut off everything to its right. Use the same formula everywhere and treat a missing neighbour (outside the grid) as 0. The only seed is the start: 1 if it is open, 0 if it is blocked.

## Hint 3

```
f = rows x cols of 0      (one fresh list per row)
for r in 0..rows-1:
    for c in 0..cols-1:
        if grid[r][c] == 1:        f[r][c] = 0
        elif r == 0 and c == 0:   f[r][c] = 1
        else:                      f[r][c] = (f[r-1][c] if r > 0 else 0) + (f[r][c-1] if c > 0 else 0)
return f[rows-1][cols-1]
```
