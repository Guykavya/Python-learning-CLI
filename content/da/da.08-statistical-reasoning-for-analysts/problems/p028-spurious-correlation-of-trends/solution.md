## Approach

Differences remove the slowly wandering level that creates the false link, leaving the period-to-period movements, which for independent series are unrelated.

## Code

```python
import numpy as np


def diff_corr(a, b):
    da, db = np.diff(np.asarray(a, float)), np.diff(np.asarray(b, float))
    if len(da) != len(db) or len(da) < 2:
        raise ValueError("need two series of the same length, at least 3 points")
    if da.std() == 0 or db.std() == 0:
        raise ValueError("r is undefined when one variable does not vary")
    return float(np.corrcoef(da, db)[0, 1])
```

## Complexity

O(n).

## Another way

Detrend, or model both series with a regression that includes time. Differencing is the simplest cure.
