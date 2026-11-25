## Approach

The covariance matrix collects how features move together; its top eigenvectors are the directions that carry the most variance.

## Code

```python
import numpy as np


def pca(X, k):
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(axis=0)
    C = Xc.T @ Xc / (len(X) - 1)
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    return V[:, order[:k]].T, w[order[:k]] / w.sum()
```

## Complexity

O(n d^2 + d^3) time.

## Another way

Take the SVD of the centred data: the right singular vectors are the components and `s^2 / (n - 1)` the variances.
