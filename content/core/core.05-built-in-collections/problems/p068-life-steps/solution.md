## Approach

Double buffering: read from the old grid, write into a brand new grid, then swap. Because the
new grid is built fresh every generation, no row is shared with the old one.

## Code

```python
r, c, g = [int(x) for x in input().split()]
grid = [list(input().strip()) for _ in range(r)]
for _ in range(g):
    new = [["."] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            live = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di or dj) and 0 <= i + di < r and 0 <= j + dj < c:
                        if grid[i + di][j + dj] == "#":
                            live += 1
            if grid[i][j] == "#" and live in (2, 3):
                new[i][j] = "#"
            elif grid[i][j] == "." and live == 3:
                new[i][j] = "#"
    grid = new
for row in grid:
    print("".join(row))
```

## Complexity

O(g × r × c × 8).

## The in-place trap

Updating `grid[i][j]` directly means that when you later count neighbours for `grid[i][j + 1]`,
you see the new value of `grid[i][j]`, not the old one. The "same time" rule is broken. A
shallow copy such as `new = grid[:]` has the same problem, because it shares the rows.
