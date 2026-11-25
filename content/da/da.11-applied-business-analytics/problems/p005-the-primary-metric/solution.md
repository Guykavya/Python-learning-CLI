## Approach

The confidence interval and the test answer slightly different questions, which is why they use different standard errors. They agree closely for large samples.

## Code

```python
import numpy as np
from scipy import stats


def two_prop(kA, nA, kB, nB, level=0.95):
    pA, pB = kA / nA, kB / nB
    diff = pB - pA
    se = np.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    pp = (kA + kB) / (nA + nB)
    z_stat = diff / np.sqrt(pp * (1 - pp) * (1 / nA + 1 / nB))
    return {"A": float(pA), "B": float(pB), "diff": float(diff), "lo": float(diff - z * se), "hi": float(diff + z * se),
            "rel_lift": float(diff / pA), "p": float(2 * stats.norm.sf(abs(z_stat)))}
```

## Complexity

O(1).

## Another way

`statsmodels.stats.proportion.proportions_ztest([kB, kA], [nB, nA])` returns the same z and p; `confint_proportions_2indep` gives other interval methods.
