## Approach

- **State:** `f[r][c]` = the cheapest cost from `(0, 0)` to `(r, c)`, counting both cells.
- **Transition:** `f[r][c] = grid[r][c] + min(f[r-1][c], f[r][c-1])`, using only the neighbours that exist.
- **Base:** `f[0][0] = grid[0][0]`; the first row and the first column are running sums.
- **Answer:** `f[rows-1][cols-1]`.

```python
def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                f[r][c] = grid[r][c]
            elif r == 0:
                f[r][c] = f[r][c - 1] + grid[r][c]          # only from the left
            elif c == 0:
                f[r][c] = f[r - 1][c] + grid[r][c]          # only from above
            else:
                f[r][c] = grid[r][c] + min(f[r - 1][c], f[r][c - 1])
    return f[rows - 1][cols - 1]
```

Row by row, left to right: when `(r, c)` is filled, the cell above (previous row) and the cell to the left (same row, earlier) are already final.

## Complexity

`O(rows * cols)` time and space; one rolling row brings the space to `O(cols)`.

## Another way

The infinity border of section 8: a table one row and one column bigger, filled with `INF`, and `f[0][1] = 0` as the seed. Then every cell uses the same line `f[r+1][c+1] = grid[r][c] + min(f[r][c+1], f[r+1][c])`, with no `if`s. The tests use that version as their checker for the big grid.
