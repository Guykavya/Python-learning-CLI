## Approach

Truncate the SVD after `k` terms: the biggest terms carry most of the matrix.

## Code

```python
import numpy as np


def low_rank(M, k):
    U, s, Vt = np.linalg.svd(np.asarray(M, dtype=float), full_matrices=False)
    return (U[:, :k] * s[:k]) @ Vt[:k]
```

## Complexity

O(m n min(m, n)) for the SVD, O(m n k) for the product.

## Another way

Sum `k` rank-one matrices `s_i u_i v_i^T`, which makes the 'layers' of the matrix visible.
