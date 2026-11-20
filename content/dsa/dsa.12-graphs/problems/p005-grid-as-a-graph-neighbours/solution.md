## Approach

A table of moves turns eight similar `if` statements into one loop. The bounds check comes **before** the grid lookup, so that negative indexes never reach `grid[...]`.

## Code

```python
STRAIGHT = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONAL = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def neighbours(grid, r, c, diagonal=False):
    rows, cols = len(grid), len(grid[0])
    moves = STRAIGHT + DIAGONAL if diagonal else STRAIGHT
    out = []
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out
```

## Complexity

`O(1)` per call: at most 8 cells are looked at. A grid of `R x C` cells has at most `4RC` (or `8RC`) edge ends, so grids are sparse graphs.

## Another way

A generator (`yield (nr, nc)`) avoids building a list; the chapter's `grid_neighbours` does that. Some solutions add a border of walls around the grid ("padding") so that no bounds check is needed.
