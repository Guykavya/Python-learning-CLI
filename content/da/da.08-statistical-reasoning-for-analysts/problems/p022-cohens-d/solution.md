## Approach

The pooled standard deviation is a weighted average of the two variances (weights `n - 1`), so a bigger group counts more. Dividing the difference by it removes the units.

## Code

```python
import numpy as np


def cohens_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / sp)
```

## Complexity

O(n).

## Another way

For very small samples Hedges' g multiplies d by a small correction factor. In reports, give d together with the interval of the raw difference.
