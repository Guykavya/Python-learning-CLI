## Approach

`np.isfinite` is the one mask that excludes all three bad values. Count what it rejects, then average what it keeps. The empty case is decided **before** averaging, so NumPy never has to warn: a function that knows "nothing is left" should say so with `nan` itself.

## Code

```python
import numpy as np


def clean_mean(x):
    x = np.asarray(x, dtype=float)
    ok = np.isfinite(x)
    n_dropped = int(x.size - np.count_nonzero(ok))
    if not ok.any():
        return float("nan"), n_dropped
    return float(x[ok].mean()), n_dropped
```

## Complexity

O(n): one mask, one count, one mean of the kept values (a copy, because a mask gives a copy).

## Another way

`np.mean(x, where=ok)` averages only where the mask is `True` without making the copy; it still warns when the mask is all `False`, so the early return stays. Returning the count is the habit of Ch. 10.4: say how much data you ignored, so nobody trusts a mean of 3 values out of 3,000.
