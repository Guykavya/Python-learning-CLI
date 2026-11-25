## Approach

Minimising the squared error makes the residual perpendicular to every column of `A`, which is `A^T (b - A x) = 0`.

## Code

```python
import numpy as np


def least_squares(A, b):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.linalg.solve(A.T @ A, A.T @ b)
```

## Complexity

O(m n^2 + n^3) time.

## Another way

`np.linalg.lstsq(A, b)` uses an SVD and is more accurate when the columns are nearly dependent.
