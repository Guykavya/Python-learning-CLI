## Approach

Three vectorised methods, one per column. `diff()` is `s - s.shift(1)`, `pct_change()` is `diff / yesterday`, and `cumsum()` accumulates. The first row has no yesterday, so both change columns start with `NaN` on their own. A zero yesterday makes `x / 0 = inf` (and `0 / 0 = NaN`): the statement wants only real numbers and gaps, so replace `inf` and `-inf` by `NaN`. Building the DataFrame from a dict keeps the column order and the index.

## Code

```python
import numpy as np
import pandas as pd


def daily_changes(s):
    return pd.DataFrame({
        "diff": s.diff(),
        "pct_change": s.pct_change().replace([np.inf, -np.inf], np.nan),
        "running_total": s.cumsum(),
    })
```

## Complexity

O(n), three passes.

## Another way

Compute the percentage by hand to see where the infinity comes from: `s.diff() / s.shift(1)`, and mask the zero denominator first: `s.diff() / s.shift(1).where(s.shift(1) != 0)`. That divides only where yesterday was non-zero, so no `inf` is ever created.
