## Approach

Mean plus or minus a t multiplier times the standard error. The t quantile has `n - 1` degrees of freedom and takes `(1 + level) / 2` so that the two tails together hold `1 - level`.

## Code

```python
import numpy as np
from scipy import stats


def ci_mean(x, level=0.95):
    x = np.asarray(x, dtype=float)
    n = len(x)
    se = x.std(ddof=1) / np.sqrt(n)
    h = stats.t.ppf((1 + level) / 2, df=n - 1) * se
    return float(x.mean() - h), float(x.mean() + h)
```

## Complexity

O(n).

## Another way

`stats.t.interval(level, df=n - 1, loc=x.mean(), scale=stats.sem(x))` returns the same interval in one call.
