## Approach

The spread of the statistic across resamples stands in for its spread across real repeated samples.

## Code

```python
import numpy as np


def bootstrap_ci(x, stat=np.mean, level=0.95, reps=2000, seed=0):
    x = np.asarray(x, dtype=float)
    n = len(x)
    rng = np.random.default_rng(seed)
    values = np.array([stat(x[rng.integers(0, n, n)]) for _ in range(reps)])
    a = (1 - level) / 2
    return float(np.quantile(values, a)), float(np.quantile(values, 1 - a))
```

## Complexity

O(reps n).

## Another way

The bootstrap standard error `std(boot_stats)` gives a normal-theory interval `stat +- 1.96 se`; the percentile interval also handles skewed statistics.
