## Approach

The sum of the ranks of the positives, minus the smallest it could possibly be (`n_pos (n_pos + 1) / 2`), counts, for each positive, how many negatives rank below it: the Mann-Whitney U statistic. Dividing by the number of pairs gives the probability.

## Code

```python
import numpy as np
from scipy.stats import rankdata


def auc_by_pairs(y, score):
    y = np.asarray(y)
    score = np.asarray(score, dtype=float)
    n_pos = int(np.sum(y == 1))
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("AUC needs both classes")
    ranks = rankdata(score)
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))
```

## Complexity

O(n log n) for the sort inside `rankdata`; O(n) memory.

## Another way

`np.argsort` plus a loop that averages the ranks of equal scores avoids SciPy. `sklearn.metrics.roc_auc_score` is the referee.
