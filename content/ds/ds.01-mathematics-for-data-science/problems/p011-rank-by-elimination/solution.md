## Approach

Forward elimination on an `m x n` matrix, counting the columns where a pivot above the tolerance exists.

## Code

```python
import numpy as np


def rank(A):
    A = np.array(A, dtype=float)
    m, n = A.shape
    tol = 1e-10 * max(float(np.abs(A).max()), 1e-300)
    r = 0
    for c in range(n):
        if r >= m:
            break
        p = r + int(np.argmax(np.abs(A[r:, c])))
        if abs(A[p, c]) <= tol:
            continue
        A[[r, p]] = A[[p, r]]
        for i in range(r + 1, m):
            A[i, c:] -= A[i, c] / A[r, c] * A[r, c:]
        r += 1
    return r
```

## Complexity

O(m n min(m, n)) time.

## Another way

Count the singular values above a tolerance (SVD), which is what `np.linalg.matrix_rank` does.
