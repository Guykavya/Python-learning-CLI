## Approach

Differentiate the sum of squares: each residual contributes `2 r_i * x_i`, and the mean divides by `n`.

## Code

```python
import numpy as np


def mse_grad(w, X, y):
    X = np.asarray(X, dtype=float)
    w = np.asarray(w, dtype=float)
    y = np.asarray(y, dtype=float)
    return 2.0 / len(y) * (X.T @ (X @ w - y))
```

## Complexity

O(n d) time.

## Another way

Verify it with `grad_check` from problem 27: that is how you find a missing 2 or a wrong sign.
