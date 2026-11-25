## Approach

Threshold the probabilities, then count the four combinations.

## Code

```python
import numpy as np


def confusion_at(y, p, threshold):
    y = np.asarray(y).astype(bool)
    pred = np.asarray(p, dtype=float) >= threshold
    return {
        "TP": int(np.sum(y & pred)),
        "FP": int(np.sum(~y & pred)),
        "FN": int(np.sum(y & ~pred)),
        "TN": int(np.sum(~y & ~pred)),
    }
```

## Complexity

O(n).

## Another way

`sklearn.metrics.confusion_matrix(y, pred)` returns the same four counts as a 2x2 array (rows actual, columns predicted; careful with the order).
