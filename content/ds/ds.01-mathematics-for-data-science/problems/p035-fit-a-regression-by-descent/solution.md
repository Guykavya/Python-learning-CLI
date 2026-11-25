## Approach

The same descent loop with the MSE gradient on the design matrix with a column of ones.

## Code

```python
import numpy as np


def fit_linear_gd(X, y, lr, steps):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    A = np.column_stack([np.ones(len(X)), X])
    w = np.zeros(A.shape[1])
    for _ in range(steps):
        w = w - lr * 2.0 / len(y) * (A.T @ (A @ w - y))
    return w
```

## Complexity

O(steps n d).

## Another way

`np.linalg.lstsq(A, y)` gives the answer in one step; descent is what you use when `lstsq` is too big or the model is not linear.
