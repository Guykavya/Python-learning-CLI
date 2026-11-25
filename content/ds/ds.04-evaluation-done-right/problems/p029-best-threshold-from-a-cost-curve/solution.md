## Approach

Price every candidate threshold on validation data and keep the cheapest. The strict `<` keeps the first threshold on a tie.

## Code

```python
import numpy as np


def best_threshold(y_val, p_val, cost, grid):
    y = np.asarray(y_val).astype(bool)
    p = np.asarray(p_val, dtype=float)
    best_t, best_c = None, np.inf
    for t in grid:
        pred = p >= t
        tp = np.sum(pred & y); fp = np.sum(pred & ~y)
        fn = np.sum(~pred & y); tn = np.sum(~pred & ~y)
        c = tn * cost.get("tn", 0) + fp * cost.get("fp", 0) + fn * cost.get("fn", 0) + tp * cost.get("tp", 0)
        if c < best_c:
            best_t, best_c = t, c
    return float(best_t)
```

## Complexity

O(len(grid) * n).

## Another way

Sort by probability once and sweep the threshold, updating the counts incrementally: O(n log n) for every possible threshold.
