## Approach

Allocate the result, then fill each entry with a row-by-column dot product after checking the inner sizes.

## Code

```python
import numpy as np


def matmul(A, B):
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    m, n = A.shape
    n2, p = B.shape
    if n != n2:
        raise ValueError(f"shapes {A.shape} and {B.shape} do not fit")
    C = np.zeros((m, p))
    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]
    return C
```

## Complexity

O(m n p) time, O(m p) space for the result.

## Another way

One loop over rows with `A[i] @ B` per row, or a single `@`: the loops show what the library does.
