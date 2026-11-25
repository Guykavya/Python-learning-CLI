## Approach

The difficulty of the particular rows affects both models in the same way. Resampling the pair together cancels that shared noise, so the interval of the difference is much narrower than the intervals of the two AUCs separately.

## Code

```python
import numpy as np
from sklearn.metrics import roc_auc_score


def paired_difference(y, p_model, p_base, reps=500, seed=0):
    y = np.asarray(y)
    p_model = np.asarray(p_model)
    p_base = np.asarray(p_base)
    rng = np.random.default_rng(seed)
    n = len(y)
    diffs = []
    for _ in range(reps):
        idx = rng.integers(0, n, n)
        if len(np.unique(y[idx])) < 2:
            continue
        diffs.append(roc_auc_score(y[idx], p_model[idx]) - roc_auc_score(y[idx], p_base[idx]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(np.mean(diffs)), float(lo), float(hi)
```

## Complexity

`2 * reps` AUC computations.

## Another way

DeLong's test gives an analytic interval for correlated AUCs; the bootstrap is simpler and works for any metric.
