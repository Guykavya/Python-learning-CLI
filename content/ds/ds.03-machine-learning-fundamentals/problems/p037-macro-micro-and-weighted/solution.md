## Approach

`F1 = 2 TP / (2 TP + FP + FN)` is the harmonic-mean formula rewritten in counts, and it handles the zero-precision, zero-recall case without a special branch (apart from an empty denominator). Compute per class, then average three ways.

## Code

```python
import numpy as np


def multiclass_f1(y, p):
    y = np.asarray(y)
    p = np.asarray(p)
    if y.shape != p.shape:
        raise ValueError("y and p must have the same length")
    classes = np.unique(np.concatenate([y, p]))
    f1s, supports = [], []
    tp_all = fp_all = fn_all = 0
    for c in classes:
        tp = int(np.sum((y == c) & (p == c)))
        fp = int(np.sum((y != c) & (p == c)))
        fn = int(np.sum((y == c) & (p != c)))
        denom = 2 * tp + fp + fn
        f1s.append(2 * tp / denom if denom else 0.0)
        supports.append(int(np.sum(y == c)))
        tp_all += tp
        fp_all += fp
        fn_all += fn
    f1s = np.array(f1s)
    supports = np.array(supports)
    denom = 2 * tp_all + fp_all + fn_all
    return {
        "macro": float(f1s.mean()),
        "micro": float(2 * tp_all / denom) if denom else 0.0,
        "weighted": float(np.sum(f1s * supports) / supports.sum()),
    }
```

## Complexity

O(n * number of classes).

## Another way

`sklearn.metrics.f1_score(y, p, average="macro" | "micro" | "weighted", zero_division=0)`. For single-label problems the micro F1 equals the accuracy.
