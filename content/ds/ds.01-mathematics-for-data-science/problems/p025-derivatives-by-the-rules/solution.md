## Approach

Look the name up in a dictionary of derivative functions; each one is the textbook rule.

## Code

```python
import math


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def derivative_of(name):
    table = {
        "poly": lambda x: 3 * x ** 2 - 2,
        "exp2x": lambda x: 2 * math.exp(2 * x),
        "log": lambda x: 1.0 / x,
        "sigmoid": lambda x: _sigmoid(x) * (1 - _sigmoid(x)),
        "product": lambda x: math.sin(x) + x * math.cos(x),
        "chain": lambda x: 2 * x * math.cos(x ** 2),
    }
    return table[name]
```

## Complexity

Constant time per call.

## Another way

Check each derivative with `num_deriv` (problem 23): disagreement means you made an algebra slip.
