## Approach

Two passes (section 9, "Reconstructing a path in a grid"):

1. **Forward:** fill `f[r][c]` = the cheapest cost from the start to `(r, c)`, as in minimum path sum.
2. **Backward:** from the end, repeatedly step to the predecessor with the smaller `f`. That predecessor is the one the `min` chose when `f[r][c]` was computed, so it lies on a cheapest path. Reverse the collected cells.

```python
def min_path(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                best_prev = 0
            elif r == 0:
                best_prev = f[r][c - 1]
            elif c == 0:
                best_prev = f[r - 1][c]
            else:
                best_prev = min(f[r - 1][c], f[r][c - 1])
            f[r][c] = grid[r][c] + best_prev
    # walk back from the end, always to the cheaper predecessor
    r, c = rows - 1, cols - 1
    route = [(r, c)]
    while (r, c) != (0, 0):
        if r == 0:
            c -= 1
        elif c == 0:
            r -= 1
        elif f[r - 1][c] <= f[r][c - 1]:
            r -= 1
        else:
            c -= 1
        route.append((r, c))
    route.reverse()
    return f[rows - 1][cols - 1], route
```

Compare `f`, not `grid`: `f` is the cost of the **whole** best path into a neighbour, while `grid` is only that one cell. In `[[0,0,0],[9,9,3],[9,1,0]]` the left neighbour of the end cell costs only 1, but the best path into it costs 10; the cell above costs 3 and its best path costs 3. Comparing `grid` would step left and return a route of cost 10.

When `f` ties, both neighbours are on cheapest paths, which is why the tests accept any legal route with the minimum cost.

## Complexity

`O(rows * cols)` time and space for the table, plus `O(rows + cols)` for the walk back. The table cannot be rolled away here: the walk back needs every row.

## Another way

Parent pointers (section 9, method 1): while filling `f`, store in `came[r][c]` which neighbour won (`"up"` or `"left"`). The walk back then just follows `came`. It costs another table of the same size, but the walk needs no comparisons.
