## Approach

The bootstrap treats the sample as a stand-in for the population: resampling it shows how much the statistic would vary. The percentile interval reads the interval straight from the replicates.

## Code

```python
import numpy as np


def bootstrap_ci(x, stat, B=2000, level=0.95, rng=None):
    rng = np.random.default_rng() if rng is None else rng
    x = np.asarray(x)
    boots = np.array([stat(rng.choice(x, len(x), replace=True)) for _ in range(B)])
    a = (1 - level) / 2
    lo, hi = np.quantile(boots, [a, 1 - a])
    return float(lo), float(hi)
```

## Complexity

O(B x n).

## Another way

Vectorise: `rng.choice(x, (B, len(x)))` then `stat(..., axis=1)` is much faster for the mean. The bootstrap needs a decent sample: with 10 values it cannot invent information that is not there.
