## Approach

Fit by the normal equations, get the residuals, divide their sum of squares by the degrees of freedom, scale the inverse of `X^T X`, and take square roots of the diagonal.

## Code

```python
import numpy as np


def ols_se(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, p = X.shape
    xtx = X.T @ X
    b = np.linalg.solve(xtx, X.T @ y)
    resid = y - X @ b
    sigma2 = float(resid @ resid) / (n - p)
    return np.sqrt(np.diag(sigma2 * np.linalg.inv(xtx)))
```

## Complexity

O(n p^2 + p^3).

## Another way

`sm.OLS(y, X).fit().bse` gives the same numbers; use it as a referee. In practice you never invert `X^T X` for anything larger than a check like this.
