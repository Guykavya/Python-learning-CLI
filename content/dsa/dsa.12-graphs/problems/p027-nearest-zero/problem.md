# Nearest 0 (multi-source BFS)

`mat` is a matrix (a list of rows, each a list of `0` and `1`). It contains at least one `0`.

Write `nearest_zero(mat)`. It returns a **new** matrix of the same size in which every cell holds the number of steps (up, down, left or right) from that cell to the nearest `0`. A `0` cell holds `0`. The input matrix must not change.

This is multi-source BFS (chapter section 3): instead of one search per cell, start **one** BFS from **all** zeros at once. The first time the wave reaches a cell is its distance.

## Example

```python
>>> nearest_zero([[0, 0, 0],
...               [0, 1, 0],
...               [1, 1, 1]])
[[0, 0, 0], [0, 1, 0], [1, 2, 1]]
>>> nearest_zero([[1, 1, 1],
...               [1, 1, 1],
...               [1, 1, 0]])
[[4, 3, 2], [3, 2, 1], [2, 1, 0]]
```

## Constraints

- `1 <= rows, cols <= 300`, at least one `0`.
- `O(rows * cols)` time. A 300 x 300 matrix with a single `0` in a corner is run with a **time limit**: a separate BFS (or a scan of all zeros) for every `1` cell is far too slow there.

## Think about

Why does a BFS that starts with all zeros in the queue give each cell the distance to its **nearest** zero, and not to some other zero? When should a cell get its distance: when it is pushed or when it is popped?
