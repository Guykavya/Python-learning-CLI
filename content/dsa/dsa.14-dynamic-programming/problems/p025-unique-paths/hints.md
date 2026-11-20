## Hint 1

The last move into `(r, c)` came either from the cell above, `(r - 1, c)`, or from the cell on the left, `(r, c - 1)`. Those two groups of paths do not overlap. So `f[r][c] = f[r-1][c] + f[r][c-1]`. What is `f` on the first row, where there is no cell above?

## Hint 2

The first row and the first column are all 1s (only one straight path reaches them). Fill the rest row by row, left to right, so that "above" and "left" are always ready. The answer is the bottom-right cell.

## Hint 3

One rolling row, as in section 6:

```
row = [1] * cols
repeat rows - 1 times:
    for c in 1 .. cols-1:
        row[c] = row[c] + row[c-1]     # above + left
return row[cols-1]
```
