## Approach

Vectorise: all `sims` experiments are arrays. Guard the division where the SE is zero. The mean of the Boolean "p < 0.05" is the estimated power.

## Code

```python
import numpy as np
from scipy import stats


def power(p0, p1, n, sims, rng):
    ka = rng.binomial(n, p0, sims)
    kb = rng.binomial(n, p1, sims)
    pp = (ka + kb) / (2 * n)
    se = np.sqrt(pp * (1 - pp) * (2 / n))
    z = np.divide((kb - ka) / n, se, out=np.zeros(sims), where=se > 0)
    return float(np.mean(2 * stats.norm.sf(np.abs(z)) < 0.05))
```

## Complexity

O(sims).

## Another way

`statsmodels.stats.power.NormalIndPower().power(proportion_effectsize(p1, p0), n, 0.05)` gives a formula answer; the simulation agrees within Monte Carlo noise and extends to cases without a formula.

## Pitfall to remember

A "not significant" result from a small experiment (power 12%) says almost nothing: look at the interval.
