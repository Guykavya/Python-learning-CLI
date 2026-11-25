## Approach

This is da.01's IQR rule in three array lines. `np.percentile(x, [25, 75])` returns both quartiles with the default `linear` method, which equals `statistics.quantiles(..., method="inclusive")` (Ch. 14.2). One mask marks the outliers; `np.where` builds a **new** array choosing the median where the mask is true and the original value elsewhere. Summing a boolean mask counts its `True` values.

## Code

```python
import numpy as np


def cap_outliers(x, k=1.5):
    x = np.asarray(x, dtype=float)
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    outside = (x < low) | (x > high)
    cleaned = np.where(outside, np.median(x), x)
    return cleaned, int(np.count_nonzero(outside))
```

## Complexity

O(n log n) at most for the percentiles and the median (NumPy uses partial sorting, close to O(n) in practice), O(n) for the mask and `np.where`.

## Another way

`cleaned = x.astype(float)` (a copy) followed by `cleaned[outside] = np.median(x)` assigns through the mask (Ch. 8.3). Replacing outliers by the median is one choice among several; "winsorising" clips them to the fences instead (`np.clip(x, low, high)`). Whatever you choose, report `n_replaced`: a cleaning step that hides how much it changed is a trap for the next reader.
