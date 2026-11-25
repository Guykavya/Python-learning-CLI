## Approach

Sort the variance shares (the SVD already does), form the cumulative sum, find where it first reaches the target.

## Code

```python
import numpy as np


def components_for(X, share):
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(axis=0)
    s = np.linalg.svd(Xc, compute_uv=False)
    cum = np.cumsum(s ** 2) / np.sum(s ** 2)
    return int(np.argmax(cum >= share - 1e-12)) + 1
```

## Complexity

O(n d min(n, d)) time for the SVD.

## Another way

Plot the cumulative explained variance (a scree plot) and read the elbow.
