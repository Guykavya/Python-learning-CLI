## Approach

Repeated multiplication amplifies the component along the biggest eigenvalue most; normalising keeps the numbers finite.

## Code

```python
import numpy as np


def power_iteration(A, steps=500, seed=0):
    A = np.asarray(A, dtype=float)
    rng = np.random.default_rng(seed)
    v = rng.normal(size=A.shape[0])
    v /= np.linalg.norm(v)
    for _ in range(steps):
        w = A @ v
        v = w / np.linalg.norm(w)
    return float(v @ A @ v), v
```

## Complexity

O(steps n^2) time for dense `A`.

## Another way

Apply the iteration to the inverse (`inverse iteration`) to find the smallest eigenvalue instead.
