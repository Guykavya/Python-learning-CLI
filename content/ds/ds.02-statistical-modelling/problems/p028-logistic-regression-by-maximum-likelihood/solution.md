## Approach

Each Newton step solves a weighted least-squares problem, which is why the method is also called iteratively reweighted least squares. It converges in a handful of steps on well-behaved data.

## Code

```python
import numpy as np


def fit_logit(X, y, max_iter=50, tol=1e-10):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    b = np.zeros(X.shape[1])
    for _ in range(max_iter):
        p = 1.0 / (1.0 + np.exp(-(X @ b)))
        grad = X.T @ (y - p)
        hess = X.T @ (X * (p * (1.0 - p))[:, None])
        step = np.linalg.solve(hess, grad)
        b = b + step
        if np.max(np.abs(step)) < tol:
            break
    return b
```

## Complexity

Each step costs O(n p^2 + p^3); about 5-8 steps are needed.

## Another way

`scipy.optimize.minimize` on the negative log-likelihood, or `sm.Logit(...).fit()`, which does exactly this Newton iteration.
