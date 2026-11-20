# Grid as a graph: neighbours

A grid is a graph you never build: each open cell is a vertex, and its neighbours are computed when they are needed (chapter section 2, "A grid is a graph you do not build").

The grid is a list of equal-length strings. `"#"` is a wall; every other character is an open cell. Write `neighbours(grid, r, c, diagonal=False)`. It returns a **list** of `(row, col)` pairs: the open cells next to `(r, c)` that lie inside the grid.

The order is fixed:

1. up `(r-1, c)`, down `(r+1, c)`, left `(r, c-1)`, right `(r, c+1)`;
2. only if `diagonal=True`, then: up-left `(r-1, c-1)`, up-right `(r-1, c+1)`, down-left `(r+1, c-1)`, down-right `(r+1, c+1)`.

The cell `(r, c)` itself is never in the answer. Whether `(r, c)` is a wall does not matter: only the neighbours are checked.

## Example

```python
>>> GRID = ["..#.",
...         ".##.",
...         "...."]
>>> neighbours(GRID, 0, 0)
[(1, 0), (0, 1)]
>>> neighbours(GRID, 2, 1)
[(2, 0), (2, 2)]
>>> neighbours(GRID, 2, 1, diagonal=True)
[(2, 0), (2, 2), (1, 0)]
```

`(2, 1)` has the wall `(1, 1)` above it and no row below. With diagonals, `(1, 0)` is open and `(1, 2)` is a wall.

## Constraints

`1 <= rows, cols <= 1000`. `O(1)` per call.
