## Approach

The pooled rate is the ratio of two sums over the same set of cohorts, which is the retention of "all customers who could have been observed at month `k`". Mixing mature and immature cohorts in either the numerator or the denominator would bias the curve.

## Code

```python
import numpy as np
import pandas as pd


def pooled_retention(active, sizes, ks):
    out = {}
    for k in ks:
        if k not in active.columns:
            out[k] = np.nan
            continue
        col = active[k]
        ok = col.notna()
        out[k] = float(col[ok].sum() / sizes[ok].sum()) if ok.any() else np.nan
    return pd.Series(out, dtype=float)
```

## Complexity

O(cohorts x len(ks)).

## Another way

Add the Wilson interval of each pooled proportion (as the chapter does) to show how uncertain the late months are: few cohorts mature, so the numbers are noisy.
