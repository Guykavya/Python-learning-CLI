## Approach

Estimate the mean, estimate its standard error from the data, and widen by the t quantile because the standard deviation itself is estimated.

## Code

```python
import math

import numpy as np


def mean_ci(x, level, t_ppf):
    x = np.asarray(x, dtype=float)
    n = len(x)
    se = x.std(ddof=1) / math.sqrt(n)
    t = t_ppf(0.5 + level / 2, n - 1)
    return float(x.mean() - t * se), float(x.mean() + t * se)
```

## Complexity

O(n).

## Another way

For large `n` the t quantile approaches 1.96 and the interval equals the z-interval.
