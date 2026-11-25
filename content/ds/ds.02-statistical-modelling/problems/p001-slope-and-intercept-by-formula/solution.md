## Approach

Centre both variables, take the cross-product sum over the squared-x sum. The line always passes through the point of means, which gives the intercept.

## Code

```python
import numpy as np


def simple_fit(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xm, ym = x.mean(), y.mean()
    sxx = float(np.sum((x - xm) ** 2))
    if sxx == 0:
        raise ValueError("x has no spread")
    slope = float(np.sum((x - xm) * (y - ym)) / sxx)
    return float(ym - slope * xm), slope
```

## Complexity

O(n) time, O(n) extra space for the centred arrays.

## Another way

`cov(x, y) / var(x)` with the same `ddof` in both gives the same slope. `np.polyfit(x, y, 1)` returns `[slope, intercept]` (note the order).
