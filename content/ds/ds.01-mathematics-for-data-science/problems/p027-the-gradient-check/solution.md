## Approach

Estimate every partial derivative numerically and measure how far your gradient is from it, relative to their size.

## Code

```python
import numpy as np


def grad_check(f, grad, p, h=1e-5):
    p = np.asarray(p, dtype=float)
    a = np.asarray(grad(p), dtype=float)
    num = np.zeros_like(p)
    for i in range(len(p)):
        step = np.zeros_like(p)
        step[i] = h
        num[i] = (f(p + step) - f(p - step)) / (2 * h)
    denom = np.linalg.norm(a) + np.linalg.norm(num)
    if denom == 0:
        return 0.0
    return float(np.linalg.norm(a - num) / max(denom, 1e-12))
```

## Complexity

2 d evaluations of `f` for `d` coordinates.

## Another way

Check a few random directions instead of every coordinate when `d` is huge.
