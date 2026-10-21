## Approach

Each row must be its own list object. A comprehension evaluates `["."] * cols` once per row,
giving separate lists. Then marking is just `grid[r][c] = "#"`.

## Code

```python
rows, cols = [int(x) for x in input().split()]
grid = [["."] * cols for _ in range(rows)]
k = int(input())
for _ in range(k):
    r, c = [int(x) for x in input().split()]
    grid[r][c] = "#"
for row in grid:
    print("".join(row))
```

## Why not `[["."] * cols] * rows`

The outer `* rows` copies a **reference** to one row `rows` times. All rows are the same list,
so a change through `grid[0]` also shows through `grid[1]` and `grid[2]`.

## Complexity

Building is O(rows × cols); each mark is O(1).
