## Approach

Part 1 reproduces the identical summaries. Part 2 turns the three things you would look for in a plot into numbers: curvature (the quadratic helps a lot), leverage (one extreme x), outliers (one huge residual relative to the typical one).

## Code

```python
import numpy as np


def _check(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) != len(y) or len(x) < 3 or x.std() == 0:
        raise ValueError("need equal lengths, at least 3 points and a varying x")
    return x, y


def pair_summary(x, y):
    x, y = _check(x, y)
    slope, intercept = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    return float(x.mean()), float(y.mean()), float(x.var(ddof=1)), float(r), float(slope), float(intercept)


def looks_linear(x, y):
    x, y = _check(x, y)
    A = np.column_stack([np.ones_like(x), x])
    res = y - A @ np.linalg.lstsq(A, y, rcond=None)[0]
    if np.abs(res).max() < 1e-9 * (1 + np.ptp(y)):
        return True                                  # an exact line: nothing to check
    A2 = np.column_stack([A, x ** 2])
    res2 = y - A2 @ np.linalg.lstsq(A2, y, rcond=None)[0]
    curvature = 1 - (res2 ** 2).sum() / (res ** 2).sum()
    leverage = np.diag(A @ np.linalg.inv(A.T @ A) @ A.T).max()
    mad = np.median(np.abs(res))
    outlier = np.abs(res).max() / mad if mad > 0 else np.inf
    return bool(curvature < 0.5 and leverage < 0.5 and outlier < 5)
```

## Complexity

O(n) for fixed model size.

## Another way

Just plot it: the numbers above automate what a scatter plot shows at a glance. Always plot before you trust r.
