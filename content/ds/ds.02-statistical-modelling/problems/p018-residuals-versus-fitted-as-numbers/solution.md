## Approach

Group residuals by the size of the fitted value, not by row order, then compare the spread of the top group with the bottom group.

## Code

```python
import numpy as np


def funnel_ratio(result):
    fitted = np.asarray(result.fittedvalues)
    resid = np.asarray(result.resid)
    lo, hi = np.quantile(fitted, [1 / 3, 2 / 3])
    top = resid[fitted >= hi]
    bottom = resid[fitted <= lo]
    return float(np.std(top, ddof=1) / np.std(bottom, ddof=1))
```

## Complexity

O(n log n) for the quantiles.

## Another way

Breusch-Pagan (section 9.5) tests the same idea formally; the ratio is easy to read and to put in a report next to the plot.
