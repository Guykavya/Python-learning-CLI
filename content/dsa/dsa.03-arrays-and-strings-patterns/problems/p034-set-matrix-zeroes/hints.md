## Hint 1

What goes wrong if you scan the grid and clear a row and a column the moment you see a zero? Try it on the
example: what happens when the scan reaches row 2, column 3?

## Hint 2

Split the work into two passes. Pass 1 only **reads**: mark which rows and which columns contain a zero (two lists
of `True`/`False`). Pass 2 only **writes**: a cell becomes 0 if its row or its column is marked.

## Hint 3

```
zero_row = [False] * r; zero_col = [False] * c
for each cell (i, j): if grid[i][j] == 0: zero_row[i] = True; zero_col[j] = True
for each cell (i, j): if zero_row[i] or zero_col[j]: grid[i][j] = 0
print the grid
```
