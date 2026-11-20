## Approach

- **State:** `f[r][c]` = the number of paths from `(0, 0)` to `(r, c)`.
- **Transition:** `f[r][c] = f[r-1][c] + f[r][c-1]` (the last move came from above or from the left).
- **Base:** the first row and the first column are 1.
- **Answer:** `f[rows-1][cols-1]`.

Each row depends only on the row above, so one list is enough. Before the update `row[c]` still holds the value from the row above; `row[c - 1]` has just been updated, so it is the cell on the left in the current row (section 6).

```python
def unique_paths(rows, cols):
    row = [1] * cols                     # first row: one way to each cell
    for r in range(1, rows):
        for c in range(1, cols):
            row[c] = row[c] + row[c - 1]  # above (old row[c]) + left (new row[c-1])
    return row[cols - 1]
```

For `rows = 1` the outer loop runs zero times and the answer is `row[cols - 1] = 1`; for `cols = 1` the inner loop runs zero times and the answer stays 1.

## Complexity

`O(rows * cols)` additions, `O(cols)` memory. (The numbers grow to hundreds of digits, so each addition is not quite `O(1)`, but it is fast.)

## Another way

Every path is a word of `rows - 1` letters D and `cols - 1` letters R, in any order. Choosing the positions of the D's gives `comb(rows + cols - 2, rows - 1)` paths, which the tests use as the check. The DP is still the method to learn: it keeps working when the grid has obstacles (next problem), where no formula exists.
