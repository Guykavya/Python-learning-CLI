## Hint 1

After you make the copy, change one cell of the copy and print the original. Does the original
change? If so, your copy shares rows.

## Hint 2

`grid.copy()`, `grid[:]` and `list(grid)` are all shallow. Copy each row:
`[row[:] for row in grid]`, or use `copy.deepcopy(grid)`.

## Hint 3

To count differences, compare `grid[i][j]` with `work[i][j]` for every position.
