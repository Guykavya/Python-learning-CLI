## Approach

Sort so that each store's months are in order (text months like `"2025-03"` sort correctly). `groupby(...).pct_change()`
restarts in every store, so each store's first month is `NaN`. Growth from 0 is undefined: pandas returns `inf` for
`x / 0` and `NaN` for `0 / 0`, so replacing `±inf` with `NaN` makes both cases missing.

## Code

```python
import numpy as np
import pandas as pd


def store_growth(monthly):
    out = monthly.sort_values(["store_id", "month"], ignore_index=True)
    growth = out.groupby("store_id")["revenue"].pct_change() * 100
    out["growth_pct"] = growth.replace([np.inf, -np.inf], np.nan)
    return out
```

## Complexity

O(n log n) for the sort, O(n) for the changes.

## Another way

Build it from `shift`, which makes the zero rule visible:

```python
prev = out.groupby("store_id")["revenue"].shift(1)
out["growth_pct"] = (out["revenue"] / prev.where(prev != 0) - 1) * 100
```

`prev.where(prev != 0)` turns a zero previous month into `NaN`, so the division gives `NaN` directly.
