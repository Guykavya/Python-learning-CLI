## Approach

Functions are values, so a dict can map each symbol to the function that implements it. The
lookup replaces the whole `if`/`elif` chain, and `get` gives `None` for unknown symbols. The
rest is ordinary: call the function you found with `(a, b)`.

## Code

```python
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    """Return a / b, or None when b is 0."""
    if b == 0:
        return None
    return a / b


OPERATIONS = {"+": add, "-": subtract, "*": multiply, "/": divide}


def calculate(a, op, b):
    """Look up op in OPERATIONS and apply it to a and b; None for an unknown op."""
    func = OPERATIONS.get(op)
    if func is None:
        return None
    return func(a, b)
```

## Complexity

O(1) per calculation: one dict lookup and one call.

## Another way

The standard library's `operator` module already has these functions: `operator.add`,
`operator.sub`, `operator.mul`, `operator.truediv`. A table such as
`{"+": operator.add, ...}` saves writing them, though `truediv` raises an error on zero instead of
returning `None`.
