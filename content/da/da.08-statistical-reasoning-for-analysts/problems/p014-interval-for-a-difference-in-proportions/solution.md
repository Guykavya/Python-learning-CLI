## Approach

Variances of independent proportions add, so the SE of the difference combines both groups (not their sum of standard errors).

## Code

```python
import numpy as np


def diff_prop_ci(k1, n1, k2, n2, z=1.96):
    p1, p2 = k1 / n1, k2 / n2
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p1 - p2
    return float(d), (float(d - z * se), float(d + z * se))
```

## Complexity

O(1).

## Another way

Read the interval against zero (or better, against the minimum effect of interest): if 0 is outside, the data disagree with "no difference". For small counts use a Wilson-type interval for the difference.
