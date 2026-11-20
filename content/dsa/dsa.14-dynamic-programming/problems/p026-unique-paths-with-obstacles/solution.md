## Approach

- **State:** `f[r][c]` = the number of obstacle-free paths from the start to `(r, c)`.
- **Transition:** a blocked cell has `f = 0`; an open cell has `f = up + left`, where a neighbour outside the grid counts 0.
- **Base:** `f[0][0] = 1` if the start is open (and 0 if it is blocked: the obstacle test comes first).
- **Answer:** `f[rows-1][cols-1]`.

A 0 on a blocked cell is all you need: the cells after it add that 0, so no path "flows through" the obstacle.

```python
def paths_with_obstacles(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                f[r][c] = 0                     # nobody may stand here
            elif r == 0 and c == 0:
                f[r][c] = 1                     # the start
            else:
                up = f[r - 1][c] if r > 0 else 0
                left = f[r][c - 1] if c > 0 else 0
                f[r][c] = up + left
    return f[rows - 1][cols - 1]
```

## Complexity

`O(rows * cols)` time and space; `O(cols)` with one rolling row.

## Another way

The one-row version of section 8 (Try it 7): keep `row = [0] * cols`, set `row[0] = 1` if the start is open, then for each row and each column, set `row[c] = 0` on an obstacle, else `row[c] += row[c - 1]` for `c > 0`. Before the update `row[c]` is the count from above, so `+= row[c-1]` adds the count from the left.
