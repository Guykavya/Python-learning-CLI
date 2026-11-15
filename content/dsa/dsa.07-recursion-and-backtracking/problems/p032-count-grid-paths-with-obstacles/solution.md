## Approach

Count self-avoiding walks by backtracking. The visited marks are the path; un-marking on the way back lets other paths use the cell. Each call returns the number of completions from its cell, and the root's answer is the total.

## Code

```python
def count_paths(grid):
    rows, cols = len(grid), len(grid[0])
    if grid[0][0] == "#" or grid[rows - 1][cols - 1] == "#":
        return 0
    visited = [[False] * cols for _ in range(rows)]

    def go(r, c):
        if r == rows - 1 and c == cols - 1:
            return 1
        visited[r][c] = True
        total = 0
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "." and not visited[nr][nc]:
                total += go(nr, nc)
        visited[r][c] = False
        return total

    return go(0, 0)
```

Hand check for the 2x2 grid: from the top-left you can go right then down, or down then right: 2 paths. The 3x3 open grid has 12 (chapter section 10: 1, 2, 12, 184, 8512 for n = 1 .. 5).

## Complexity

Exponential in the number of free cells (each path is visited once). Depth at most the number of free cells.

## Another way

Keep the visited cells in a `set` of `(r, c)`, or pass a bit mask of visited cells down the recursion (no un-mark needed because each call gets its own value).
