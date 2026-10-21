## Hint 1

When you find an unvisited land cell, how do you find all the cells of its island? What should one call of the fill function do?

## Hint 2

```
def fill(grid, r, c, seen):          # returns the size of the island through (r, c)
    if r or c is outside the grid: return 0
    if grid[r][c] != "#" or (r, c) in seen: return 0
    seen.add((r, c))
    return 1 + fill(r+1, c) + fill(r-1, c) + fill(r, c+1) + fill(r, c-1)
```

## Hint 3

```
def island_sizes(grid):
    seen = set()
    sizes = []
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == "#" and (r, c) not in seen:
                sizes.append(fill(grid, r, c, seen))
    return sorted(sizes, reverse=True)
```
