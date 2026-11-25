## Approach

Solve `margin = z * sd / sqrt(n)` for `n`. Round **up**: a bit more data than needed is fine, a bit less breaks the promise.

## Code

```python
import math
from scipy import stats


def _z(level):
    return stats.norm.ppf((1 + level) / 2)


def n_for_margin(sd, margin, level=0.95):
    if margin <= 0:
        raise ValueError("margin must be positive")
    return math.ceil((_z(level) * sd / margin) ** 2)


def n_for_proportion(margin, p=0.5, level=0.95):
    if margin <= 0:
        raise ValueError("margin must be positive")
    return math.ceil(_z(level) ** 2 * p * (1 - p) / margin ** 2)
```

## Complexity

O(1).

## Another way

Halving the margin multiplies `n` by 4. The formula assumes a simple random sample; real surveys need more (non-response, design effects).
