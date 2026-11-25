## Approach

Two ordinary derivatives, each with the other variable held fixed.

## Code

```python
import numpy as np


def grad_f(p):
    x, y = float(p[0]), float(p[1])
    return np.array([2 * x * y, x ** 2 + 3])
```

## Complexity

Constant time.

## Another way

Check the answer against a numerical gradient (next problem).
