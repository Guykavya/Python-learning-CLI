## Approach

The "ends exactly here" state, in two dimensions:

- **State:** `f[r][c]` = the side of the largest all-ones square with its bottom-right corner at `(r, c)`.
- **Transition:** 0 for a 0 cell; for a 1 cell, `1 + min(f[r-1][c], f[r][c-1], f[r-1][c-1])`.
- **Base:** a 1 in the first row or column has `f = 1`.
- **Answer:** the largest `f` anywhere, **squared**.

Why the minimum of three? A square of side `k` at `(r, c)` contains squares of side `k - 1` ending above, to the left and on the diagonal, so `k - 1 <= ` each of them. In the other direction, if all three are at least `k - 1`, those three squares plus the cell itself cover the whole `k` by `k` square. So the side is exactly one more than the smallest of the three. The diagonal matters: with only `min(above, left)` a 0 in the corner of the big square is missed.

```python
def maximal_square(matrix):
    rows, cols = len(matrix), len(matrix[0])
    f = [[0] * cols for _ in range(rows)]      # fresh list per row (no aliasing)
    best = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 1:
                if r == 0 or c == 0:
                    f[r][c] = 1
                else:
                    f[r][c] = 1 + min(f[r - 1][c], f[r][c - 1], f[r - 1][c - 1])
                best = max(best, f[r][c])
    return best * best
```

## Complexity

`O(rows * cols)` time and space. With one previous row and the current row (fresh list each time, so the diagonal `prev[c-1]` is still the old value), the space is `O(cols)`.

## Another way

Brute force: for every top-left cell, grow `k` while the `k` by `k` square is all ones. Correct but `O(rows * cols * min(rows, cols)^3)`; the tests use it on small grids. A middle way is to precompute prefix sums of the grid so each square check is `O(1)` (a square is all ones when its sum is `k * k`), giving `O(n^3)`, still slower than the DP.
