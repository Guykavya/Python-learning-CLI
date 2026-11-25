## Approach

Build the two sides of the normal equations and hand them to a linear solver.

## Code

```python
import numpy as np


def ols_coefs(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    return np.linalg.solve(X.T @ X, X.T @ y)
```

## Complexity

Forming `X^T X` costs O(n p^2); solving costs O(p^3).

## Another way

`np.linalg.lstsq(X, y)` or a QR factorisation is numerically safer when the columns are almost collinear; statsmodels uses a pseudo-inverse for that reason.
