## Approach

The shuffles build the distribution of the difference under "labels do not matter". The proportion at least as extreme as the observed value is the p-value. The `+1` in numerator and denominator treats the observed arrangement as one of the shuffles: a Monte Carlo p-value of exactly 0 is impossible with finitely many shuffles.

## Code

```python
import numpy as np


def permutation_p(a, b, reps, rng):
    a, b = np.asarray(a, float), np.asarray(b, float)
    pool = np.concatenate([a, b])
    n = len(a)
    d_obs = abs(a.mean() - b.mean())
    count = 0
    for _ in range(reps):
        s = rng.permutation(pool)
        if abs(s[:n].mean() - s[n:].mean()) >= d_obs - 1e-12:
            count += 1
    return (1 + count) / (reps + 1)
```

## Complexity

O(reps x (n + m)).

## Another way

`scipy.stats.permutation_test((a, b), statistic, n_resamples=reps)` does the same and also supports other statistics. The permutation test needs no normality assumption, only exchangeability under the null.
