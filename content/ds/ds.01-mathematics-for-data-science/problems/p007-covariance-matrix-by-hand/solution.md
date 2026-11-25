## Approach

Centre each column, multiply the transpose by the data to collect every pairwise sum of products, divide by `n - 1`.

## Code

```python
import numpy as np


def cov_matrix(X):
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(axis=0)
    return Xc.T @ Xc / (len(X) - 1)
```

## Complexity

O(n d^2) time, O(d^2) space for the result.

## Another way

Loop over pairs `(i, j)` and use `np.dot(Xc[:, i], Xc[:, j]) / (n - 1)`; the matrix product does all pairs at once.
