## Approach

With two index arrays, NumPy pairs the i-th row index with the i-th column index (Ch. 9.2); the result has the (broadcast) shape of the index arrays. The diagonal is the special case where both index arrays are `0, 1, ..., k-1`. Fancy indexing checks every index, so an out-of-range one raises `IndexError` without any extra code; and it always returns a copy.

## Code

```python
import numpy as np


def pick(matrix, rows, cols):
    return matrix[np.asarray(rows), np.asarray(cols)]


def diagonal_of_top(matrix, k):
    idx = np.arange(k)
    return matrix[idx, idx]
```

## Complexity

O(number of picked values), plus the copy.

## Another way

`np.diagonal(matrix)[:k]` (or `matrix.diagonal()[:k]`) gives the same values for valid `k`, but silently returns fewer values when `k` is too large, and in NumPy it is a **read-only view**, so writing into it raises. For a block instead of pairs use `np.ix_(rows, cols)` or the broadcast shape `(len(rows), 1)` against `(len(cols),)`, as the test with `[[0], [3]]` shows.
