## Approach

A loop with a convergence test, so the step count measures the difficulty of the problem.

## Code

```python
import numpy as np


def steps_to_converge(X, y, lr, tol, max_steps=100_000):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.zeros(X.shape[1])
    n = len(y)
    for step in range(max_steps):
        g = 2.0 / n * (X.T @ (X @ w - y))
        if np.linalg.norm(g) < tol:
            return step
        w = w - lr * g
    return max_steps
```

## Complexity

O(steps n d).

## Another way

The ratio of the largest to the smallest eigenvalue of `X^T X` (the condition number) predicts the step count.
