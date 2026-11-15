## Approach

A generation is a function from the old grid to a new grid. Build the new grid in a separate list, reading every
neighbour from the old one, then replace. Neighbours come from the 8 direction pairs `(di, dj)`; each one is checked
against the grid bounds **before** it is read, so the edges behave as if surrounded by dead cells.

## Code

```python
r, c, k = [int(x) for x in input().split()]
grid = [list(input().strip()) for _ in range(r)]

for _ in range(k):
    new = [["."] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            alive = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < r and 0 <= nj < c and grid[ni][nj] == "#":
                        alive += 1
            if grid[i][j] == "#":
                new[i][j] = "#" if alive in (2, 3) else "."
            else:
                new[i][j] = "#" if alive == 3 else "."
    grid = new

for row in grid:
    print("".join(row))
```

**Hand check, the edge example.** `###` on top of a 3 x 3 grid. Top corners: neighbours inside the grid are the
middle top cell and two dead cells below, so 1: they die. Top middle: 2 alive neighbours, it stays. Centre: it sees all
three, so it is born. The bottom row sees nothing, because nothing wraps around. Result: `.#.`, `.#.`, `...`.

## Complexity

O(k * r * c * 8) time: at most 10 * 100 * 100 * 8 = 800 000 checks. O(r * c) extra memory for the second grid.

## Another way

Keep a **set** of live cells. For each live cell, add 1 to a count dictionary for each of its neighbours. A cell is
alive next time if its count is 3, or if it is 2 and the cell is alive now. That only looks at cells near live ones,
which is much faster for a large, mostly empty grid. It is also the classic way to run Life on an unbounded plane.

There is also an in-place trick: encode "was alive, now dead" and "was dead, now alive" as two extra states, so that
the old value can still be read. It saves memory but is easy to get wrong; the copy is clearer.
