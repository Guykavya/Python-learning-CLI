## Approach

The formula is the one for comparing two proportions with a normal approximation. Smaller effects need many more visitors because `n` grows with `1 / mde^2`: halving the effect quadruples the sample.

## Code

```python
import math

from scipy import stats


def n_per_group(p0, mde, alpha=0.05, power=0.80):
    if p0 <= 0 or mde <= 0 or p0 + mde >= 1:
        raise ValueError("need 0 < p0 and 0 < mde and p0 + mde < 1")
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    p_bar = p0 + mde / 2
    return int(math.ceil(2 * (z_a + z_b) ** 2 * p_bar * (1 - p_bar) / mde ** 2))
```

## Complexity

O(1).

## Another way

`statsmodels.stats.power.NormalIndPower().solve_power(effect_size=proportion_effectsize(p0 + mde, p0), alpha=alpha, power=power)` uses an arcsine transformation and agrees within about 0.2%.
