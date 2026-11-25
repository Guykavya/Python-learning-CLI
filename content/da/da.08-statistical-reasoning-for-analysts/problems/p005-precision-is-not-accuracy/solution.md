## Approach

With `ddof=0` the variance is the mean squared deviation from the mean, and the mean squared error splits exactly into squared bias plus variance. With `ddof=1` the identity would be slightly off.

## Code

```python
import numpy as np


def bias_spread_rmse(estimates, truth):
    e = np.asarray(estimates, dtype=float)
    bias = e.mean() - truth
    sd = e.std()
    rmse = np.sqrt(np.mean((e - truth) ** 2))
    return float(bias), float(sd), float(rmse)
```

## Complexity

O(n).

## Another way

Repeat a sampler many times, collect the estimates and call this function: a precise-but-biased sampler shows a small `sd` and a large `bias`.
