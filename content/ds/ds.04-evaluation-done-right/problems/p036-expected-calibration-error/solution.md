## Approach

The weighted mean of the bin gaps. Weighting by size keeps a few rows in an extreme bin from dominating.

## Code

```python
import numpy as np


def ece(y, p, bins=10):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    k = np.minimum(np.floor(p * bins).astype(int), bins - 1)
    total = 0.0
    for b in np.unique(k):
        m = k == b
        total += abs(y[m].mean() - p[m].mean()) * m.sum()
    return float(total / len(y))
```

## Complexity

O(n).

## Another way

The Brier score (`mean((p - y)^2)`) mixes calibration and ranking in one number; ECE isolates calibration but depends on the binning.
