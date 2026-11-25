## Approach

Resample the validation rows, redo the choice each time, and look at the spread of the choices. A wide range warns that a "precise" threshold like 0.173 is false precision.

## Code

```python
import numpy as np


def _best(y, p, cost, grid):
    best_t, best_c = None, np.inf
    for t in grid:
        pred = p >= t
        tp = np.sum(pred & y); fp = np.sum(pred & ~y)
        fn = np.sum(~pred & y); tn = np.sum(~pred & ~y)
        c = tn * cost.get("tn", 0) + fp * cost.get("fp", 0) + fn * cost.get("fn", 0) + tp * cost.get("tp", 0)
        if c < best_c:
            best_t, best_c = t, c
    return best_t


def threshold_stability(y, p, cost, grid, reps=100, seed=0):
    y = np.asarray(y).astype(bool)
    p = np.asarray(p, dtype=float)
    rng = np.random.default_rng(seed)
    n = len(y)
    found = [_best(y[idx], p[idx], cost, grid) for idx in (rng.integers(0, n, n) for _ in range(reps))]
    lo, hi = np.percentile(found, [5, 95])
    return float(lo), float(hi)
```

## Complexity

`reps * len(grid) * n`.

## Another way

Look at the whole cost curve: if it is flat over a wide range of thresholds, the exact choice hardly matters and the instability is harmless.
