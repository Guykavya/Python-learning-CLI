## Approach

The Wilson interval is the set of true proportions that are not rejected by a z-test; it stays inside `[0, 1]` and has positive width even for `k = 0`.

## Code

```python
import numpy as np
from scipy import stats


def wilson(k, n, level=0.95):
    if n < 1 or not 0 <= k <= n:
        raise ValueError("need n >= 1 and 0 <= k <= n")
    z = stats.norm.ppf((1 + level) / 2)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(max(0.0, centre - half)), float(min(1.0, centre + half))
```

## Complexity

O(1).

## Another way

`statsmodels.stats.proportion.proportion_confint(k, n, method="wilson")`. Use Wilson as the default for proportions; the Wald interval is a classroom formula.

## Pitfall to remember

For `k = 0` an interval `(0, 0.16)` says "zero seen in 20 does not mean the rate is zero": it could be up to about 16%.
