## Approach

Estimate `lam` by the Rayleigh quotient, then test that `A v - lam v` is (almost) zero.

## Code

```python
import numpy as np


def is_eigenvector(A, v, tol=1e-8):
    A = np.asarray(A, dtype=float)
    v = np.asarray(v, dtype=float)
    vv = float(v @ v)
    if vv == 0:
        return False, None
    Av = A @ v
    lam = float(v @ Av) / vv
    ok = np.linalg.norm(Av - lam * v) <= tol * max(1.0, np.linalg.norm(Av))
    return (True, lam) if ok else (False, None)
```

## Complexity

O(n^2) time.

## Another way

Compare the direction of `A v` and `v` with the cosine similarity: it must be +1 or -1.
