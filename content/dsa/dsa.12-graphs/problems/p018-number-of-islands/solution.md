## Approach

Count components on the implicit grid graph. Every unvisited land cell starts a new search that marks the whole island; an explicit stack keeps the depth out of Python's call stack.

## Code

```python
def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1" or seen[r][c]:
                continue
            count += 1
            seen[r][c] = True
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for nr, nc in ((cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and not seen[nr][nc]:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
    return count
```

## Complexity

`O(rows * cols)` time and memory: each cell is pushed at most once and looks at 4 neighbours.

## Another way

BFS with a `deque` gives the same count. Union-Find (section 9): union every land cell with its land neighbour to the right and below, and count the roots. Sinking land in a copy (`cells = [list(row) for row in grid]`, set visited land to `"0"`) saves the `seen` table.
