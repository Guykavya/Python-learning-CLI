## Hint 1

The values strictly increase along a path, so a path can never return to a cell: that would need a value larger than itself. The "steps to a larger neighbour" form a DAG (a graph without cycles, dsa.12). On a DAG, "the longest path starting here" depends only on the cell, never on how you got there. That is exactly what makes a memo correct, and why you do **not** need a `visited` set.

## Hint 2

`f(r, c) = 1 + max(f(nr, nc))` over the neighbours `(nr, nc)` inside the grid with `matrix[nr][nc] > matrix[r][c]`. If there is no such neighbour, `f(r, c) = 1`. The answer is the maximum of `f` over all cells.

## Hint 3

```
memo = {}
def f(r, c):
    if (r, c) in memo: return memo[(r, c)]
    best = 1
    for (dr, dc) in the 4 directions:
        nr, nc = r + dr, c + dc
        if inside the grid and matrix[nr][nc] > matrix[r][c]:
            best = max(best, 1 + f(nr, nc))
    memo[(r, c)] = best
    return best
return max(f(r, c) for every cell)
```

Each cell is computed once, and each computation looks at 4 neighbours: `O(rows * cols)`.
