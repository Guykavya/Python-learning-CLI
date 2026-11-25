## Approach

Under correct randomisation each visitor is assigned to a group with the planned probability, so the counts follow a multinomial distribution. The chi-square statistic measures how far the observed counts are from the expected ones.

## Code

```python
import numpy as np
from scipy import stats


def srm_check(counts, expected_share=(0.5, 0.5)):
    share = np.asarray(expected_share, float)
    if abs(share.sum() - 1) > 1e-9:
        raise ValueError("shares must add up to 1")
    counts = np.asarray(counts, float)
    chi2, p = stats.chisquare(counts, counts.sum() * share)
    return float(chi2), float(p)


def srm_verdict(counts, expected_share=(0.5, 0.5)):
    return "MISMATCH" if srm_check(counts, expected_share)[1] < 0.001 else "ok"
```

## Complexity

O(groups).

## Another way

For two groups, a z-test on the share of group A against 0.5 gives the same p-value; the chi-square form extends to any number of groups.
