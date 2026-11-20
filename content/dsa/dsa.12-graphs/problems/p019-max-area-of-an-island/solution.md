## Approach

The island search of p018, with a counter that goes up once per popped cell. Marking on push makes sure no cell is pushed (and counted) twice.

## Code

```python
def max_area(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1" or seen[r][c]:
                continue
            seen[r][c] = True
            stack = [(r, c)]
            area = 0
            while stack:
                cr, cc = stack.pop()
                area += 1
                for nr, nc in ((cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and not seen[nr][nc]:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            best = max(best, area)
    return best
```

## Complexity

`O(rows * cols)` time and memory.

## Another way

The chapter's `islands` function returns the list of all sizes; `max(sizes, default=0)` is this answer. Union-Find with sizes gives the largest set after all unions.
