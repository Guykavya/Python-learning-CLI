## Approach

Invert only the singular values that carry real information; zero the rest, then rebuild with the factors swapped.

## Code

```python
import numpy as np


def pinv(A, cutoff=1e-10):
    U, s, Vt = np.linalg.svd(np.asarray(A, dtype=float), full_matrices=False)
    s_inv = np.zeros_like(s)
    if s.size and s.max() > 0:
        keep = s > cutoff * s.max()
        s_inv[keep] = 1.0 / s[keep]
    return (Vt.T * s_inv) @ U.T
```

## Complexity

O(m n min(m, n)) time.

## Another way

For a full-column-rank tall matrix, `(A^T A)^-1 A^T` is the same thing, but it squares the condition number (p013).
