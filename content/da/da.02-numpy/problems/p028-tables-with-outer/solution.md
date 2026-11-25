## Approach

`ufunc.outer(a, b)` builds the table of `a[i] op b[j]` for all pairs; its shape is `a.shape + b.shape`, so for two vectors `(n, m)`. It is the same as broadcasting a column `(n, 1)` against a row `(1, m)` (Ch. 11.6). For the times table, feed `np.arange(1, n + 1)` to both sides; for `n = 0` that range is empty and the table is `(0, 0)` automatically.

## Code

```python
import numpy as np


def times_table(n):
    k = np.arange(1, n + 1)
    return np.multiply.outer(k, k)


def pairwise_diff(a, b):
    return np.subtract.outer(np.asarray(a), np.asarray(b))
```

## Complexity

O(n × m) time and memory: the table itself has that many entries, so no method can do better.

## Another way

Broadcasting with `None` (`np.newaxis`): `k[:, None] * k[None, :]` and `a[:, None] - b[None, :]`. It reads the same and works for any element-wise operation, including expressions that are not a single ufunc, such as `abs(a[:, None] - b) <= 2`.
