## Approach

- **State:** `f(r, c)` = the number of cells on the longest increasing path that **starts** at `(r, c)`.
- **Transition:** `f(r, c) = 1 + max(f(nr, nc))` over the up to four neighbours with a strictly larger value; `1` if there is none.
- **Answer:** the maximum of `f` over every cell.

Why a memo is allowed here: the values strictly increase along a path, so no path can visit a cell twice. The moves form a DAG, and on a DAG the best path from a cell does not depend on the path that led to it. In an ordinary maze (moves in every direction, no increase rule) the same idea would be wrong: there you need a `visited` set, and the answer depends on what was visited.

```python
def longest_increasing_path(matrix):
    rows, cols = len(matrix), len(matrix[0])
    memo = {}

    def f(r, c):
        """Longest increasing path that starts at (r, c)."""
        if (r, c) in memo:
            return memo[(r, c)]
        best = 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + f(nr, nc))
        memo[(r, c)] = best
        return best

    return max(f(r, c) for r in range(rows) for c in range(cols))
```

For the first example, `f` of every cell is:

| | col 0 | col 1 | col 2 |
|---|---|---|---|
| row 0 | 1 | 1 | 2 |
| row 1 | 2 | 2 | 1 |
| row 2 | 3 | 4 | 2 |

`f(2, 1) = 4`: from the 1, the larger neighbours are 2 (`f = 3`) and 6 (`f = 2`); the best is `1 + 3 = 4`.

## Complexity

Each cell is computed once and looks at 4 neighbours: `O(rows * cols)` time and space. Without the memo, a DFS from every cell repeats the same sub-paths again and again, which is exponential on a matrix with many increasing routes.

## Another way

Bottom-up, with no recursion at all: process the cells in **decreasing** order of value. When a cell is processed, every larger neighbour already has its final `f`, so `f(r, c) = 1 + max(...)` can be filled directly. Sorting costs `O(rows * cols * log(rows * cols))`. This is the "topological order" of chapter section 4, found by sorting instead of by the grid's rows. It also has no recursion depth limit, so it handles a 10,000-cell snake path that would break the recursive version.

```python
def longest_increasing_path(matrix):
    rows, cols = len(matrix), len(matrix[0])
    cells = sorted(((matrix[r][c], r, c) for r in range(rows) for c in range(cols)), reverse=True)
    f = [[1] * cols for _ in range(rows)]
    for v, r, c in cells:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > v:
                f[r][c] = max(f[r][c], 1 + f[nr][nc])
    return max(max(row) for row in f)
```
