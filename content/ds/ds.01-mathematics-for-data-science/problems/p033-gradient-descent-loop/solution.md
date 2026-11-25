## Approach

Keep the current point, move it against the gradient, and remember a copy of every point.

## Code

```python
import numpy as np


def gradient_descent(grad, w0, lr, steps):
    w = np.array(w0, dtype=float)
    history = [w.copy()]
    for _ in range(steps):
        w = w - lr * np.asarray(grad(w), dtype=float)
        history.append(w.copy())
    return w, history
```

## Complexity

`steps` gradient calls.

## Another way

Stop early when the gradient norm is tiny (a convergence test) instead of always running `steps` steps.
