## Hint 1

For one cell `(i, j)`, its neighbours are `(i + di, j + dj)` for `di` and `dj` in `-1, 0, 1`, except `(0, 0)`. Which of
those may be outside the grid? What does Python do with `grid[-1]`, and why is that a problem here?

## Hint 2

All cells change at the same time. So in one generation, read **only** from the old grid and write **only** into a new
grid. At the end of the generation, the new grid becomes the old one.

## Hint 3

```
repeat k times:
    new = r x c grid of '.'
    for each cell (i, j):
        alive = number of (di, dj) != (0, 0) with 0 <= i+di < r, 0 <= j+dj < c and grid[i+di][j+dj] == '#'
        if grid[i][j] == '#': new[i][j] = '#' if alive is 2 or 3 else '.'
        else:                new[i][j] = '#' if alive == 3 else '.'
    grid = new
print each row joined
```
