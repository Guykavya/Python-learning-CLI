## Approach

Bottom-up: the state is "the cheapest path from here to the bottom".

- **State:** `g[i][j]` = the smallest sum of a path from `(i, j)` to any cell of the bottom row.
- **Transition:** `g[i][j] = triangle[i][j] + min(g[i+1][j], g[i+1][j+1])`.
- **Base:** on the bottom row `g` is the value itself.
- **Answer:** `g[0][0]`.

Every cell of row `i` has both children in row `i + 1`, so there are no edge cases, and the answer ends up in a single cell. Each row reads only the row below: one rolling list.

```python
def min_triangle_path(triangle):
    below = list(triangle[-1])                  # g on the bottom row: just the values
    for i in range(len(triangle) - 2, -1, -1):  # rows from the second-last up to the top
        row = triangle[i]
        below = [row[j] + min(below[j], below[j + 1]) for j in range(len(row))]
    return below[0]
```

Trace the example. Bottom `[4, 1, 8, 3]`. Row `[6, 5, 7]`: `[6+1, 5+1, 7+3] = [7, 6, 10]`. Row `[3, 4]`: `[3+6, 4+6] = [9, 10]`. Top: `2 + 9 = 11`.

## Complexity

`O(n^2)` time (one step per cell), `O(n)` extra memory.

## Another way

Top-down: `f[i][j]` = cheapest from the top to `(i, j)`; the parents are `(i-1, j-1)` and `(i-1, j)`, but the first cell of a row has only the second and the last cell only the first. The answer is `min(f[n-1])`. It works, but has two edge cases and a final scan, which the bottom-up direction removes. Choosing the direction that makes the answer a single cell is a useful habit.
