## Approach

Reuse the earlier pieces: clean, interval, rounding by the standard error. The formatting is part of the statistics: the same rounding for the estimate and both ends, decided by the uncertainty.

## Code

```python
import math

import numpy as np
from scipy import stats


def sig_round(value, ref):
    if ref == 0 or not math.isfinite(ref):
        return f"{value:,.0f}"
    decimals = max(0, 1 - math.floor(math.log10(abs(ref))))
    return f"{round(value, decimals):,.{decimals}f}"


def report_mean(x, label, unit="", level=0.95):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 2:
        raise ValueError("need at least 2 real values")
    se = x.std(ddof=1) / np.sqrt(n)
    h = stats.t.ppf((1 + level) / 2, df=n - 1) * se
    m = x.mean()
    return (f"{label}: {sig_round(m, se)}{unit} ({int(round(level * 100))}% CI "
            f"{sig_round(m - h, se)} to {sig_round(m + h, se)}; n = {n:,})")
```

## Complexity

O(n).

## Another way

Put the same sentence builder in a small module and use it for every number in a report, so rounding and wording stay consistent.
