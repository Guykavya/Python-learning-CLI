## Approach

Under the null the pooled rate is the best estimate of the common rate, so it goes in the standard error. The p-value is the chance of a |z| at least this large if the null were true.

## Code

```python
import numpy as np
from scipy import stats


def two_prop_test(kA, nA, kB, nB):
    pA, pB = kA / nA, kB / nB
    p = (kA + kB) / (nA + nB)
    se = np.sqrt(p * (1 - p) * (1 / nA + 1 / nB))
    if se == 0:
        return 0.0, 1.0
    z = (pA - pB) / se
    return float(z), float(2 * stats.norm.sf(abs(z)))
```

## Complexity

O(1).

## Another way

`statsmodels.stats.proportion.proportions_ztest([kA, kB], [nA, nB])` returns the same pair. Use the interval of problem 14 alongside the p-value: the p-value says whether, the interval says how much.

## Pitfall to remember

A large p-value is not evidence of "no effect" (problem 21 on power).
