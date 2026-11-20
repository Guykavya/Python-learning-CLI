# Longest path in a matrix (memo DFS)

`matrix` is a list of rows of integers. From a cell you may step **up, down, left or right** (no diagonals, no wrapping around the edges), but only to a neighbour with a **strictly larger** value. Write `longest_increasing_path(matrix)` that returns the number of cells on the longest such path. A single cell is a path of length 1.

This is not one of the right/down grids of chapter section 8: you may move in all four directions, so there is no row-by-row order to fill a table in. Use top-down memoisation (chapter section 3) instead.

## Example

```python
>>> longest_increasing_path([[9, 9, 4],
...                          [6, 6, 8],
...                          [2, 1, 1]])
4
>>> longest_increasing_path([[3, 4, 5],
...                          [3, 2, 6],
...                          [2, 2, 1]])
4
>>> longest_increasing_path([[7]])
1
>>> longest_increasing_path([[5, 5],
...                          [5, 5]])        # equal values: no step is allowed
1
```

In the first matrix the path is `1 → 2 → 6 → 9` (bottom-middle, bottom-left, middle-left, top-left). In the second it is `3 → 4 → 5 → 6`.

## Constraints

- `1 <= rows, cols <= 150`; values from `-10**6` to `10**6`.
- A plain DFS from every cell is exponential. Your function must finish a 150 by 150 matrix in a few seconds.
- The longest path in the tests has at most 700 cells, so a memoised recursion stays below Python's recursion limit.

## Think about

1. Let `f(r, c)` be the longest path that **starts** at `(r, c)`. Write it in terms of the neighbours' `f`.
2. Can a path ever come back to a cell it has already visited? Why does that matter for memoisation? (Compare with a maze, where you would need a `visited` set.)
3. Every cell's `f` is needed by up to four neighbours. How many times does your function compute each `f(r, c)`?
