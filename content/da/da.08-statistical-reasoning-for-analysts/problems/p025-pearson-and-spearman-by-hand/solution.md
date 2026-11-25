## Approach

Pearson is covariance divided by the product of spreads. Spearman needs only ranks, so it ignores the shape of the relationship and is not moved by one huge value. Average ranks for ties make the two agree with SciPy.

## Code

```python
import numpy as np
from scipy.stats import rankdata


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need two variables of the same length, at least 2 points")
    dx, dy = x - x.mean(), y - y.mean()
    denom = np.sqrt((dx ** 2).sum() * (dy ** 2).sum())
    if denom == 0:
        raise ValueError("r is undefined when one variable does not vary")
    return float((dx * dy).sum() / denom)


def spearman(x, y):
    return pearson(rankdata(x), rankdata(y))
```

## Complexity

O(n) for Pearson, O(n log n) for the ranks.

## Another way

`np.corrcoef` and `scipy.stats.pearsonr/spearmanr` do the same; writing it by hand once makes the meaning clear.
