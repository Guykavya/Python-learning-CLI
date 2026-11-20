## Hint 1

Fix the bottom-right corner. `f[r][c]` = the side of the biggest all-ones square whose bottom-right corner is `(r, c)`. If `matrix[r][c]` is 0, `f[r][c] = 0`. On the first row or column a 1 gives `f = 1` (no room to grow). What about an inner cell with a 1?

## Hint 2

Draw a square of side `k` with corner `(r, c)`. Take away the last row: a square of side `k - 1` ends at `(r - 1, c)`. Take away the last column: one ends at `(r, c - 1)`. Take away both: one ends at `(r - 1, c - 1)`. So `k - 1` is at most each of the three values, and the smallest of them is the limit: `f[r][c] = 1 + min(above, left, diagonal)`.

## Hint 3

```
best = 0
for r, for c:
    if matrix[r][c] == 1:
        f[r][c] = 1 if r == 0 or c == 0 else 1 + min(f[r-1][c], f[r][c-1], f[r-1][c-1])
        best = max(best, f[r][c])
return best * best
```
