## Approach

Ask statsmodels for the influence measures, compare with the threshold, and order the flagged rows by importance.

## Code

```python
import numpy as np


def influential_points(result, threshold=None):
    n = int(result.nobs)
    if threshold is None:
        threshold = 4 / n
    cooks = np.asarray(result.get_influence().cooks_distance[0])
    order = np.argsort(-cooks)
    return [int(i) for i in order if cooks[i] > threshold]
```

## Complexity

O(n log n) for the sort (the influence computation itself is O(n p^2)).

## Another way

Compute Cook's distance by hand: `D_i = (r_i^2 / (p * s^2)) * h_i / (1 - h_i)^2`, with `r_i` the residual and `h_i` the leverage.
