## Approach

Scan every cell. Each unseen land cell starts a new island; a recursive flood fill from it marks
every connected land cell as seen and adds up their count. The fill's base cases reject cells
outside the grid (checked **before** indexing, because negative indices wrap around), water, and
cells already seen. Marking a cell before recursing into its neighbours stops infinite back and
forth. The visited set is created inside `island_sizes`, so every call starts clean and the grid is
only read.

## Code

```python
def fill(grid, r, c, seen):
    """Mark the island through (r, c) as seen and return its size (0 if not unseen land)."""
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[r]):
        return 0
    if grid[r][c] != "#" or (r, c) in seen:
        return 0
    seen.add((r, c))
    return (1 + fill(grid, r + 1, c, seen) + fill(grid, r - 1, c, seen)
            + fill(grid, r, c + 1, seen) + fill(grid, r, c - 1, seen))


def island_sizes(grid):
    """Return the sizes of the islands of '#' cells (4-directional), largest first."""
    seen = set()
    sizes = []
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == "#" and (r, c) not in seen:
                sizes.append(fill(grid, r, c, seen))
    return sorted(sizes, reverse=True)


def count_islands(grid):
    """Return the number of islands in grid."""
    return len(island_sizes(grid))
```

## Complexity

O(rows × cols): every cell is filled at most once. The recursion depth can reach the island size (400 for a full 20×20 grid), within the default limit; for huge maps use an explicit stack.

## Another way

Replace the recursion with an explicit stack (a list): push the start cell, then repeatedly pop a
cell and push its unseen land neighbours. Same visiting order idea, no recursion limit. The DSA
modules call these depth-first and breadth-first search.
