## Approach

Functions can be stored in a list like any other value. Loop over the list and call each one on the same value.

## Code

```python
def call_all(funcs, value):
    """Return [f(value) for each f in funcs]."""
    results = []
    for f in funcs:
        results.append(f(value))
    return results


CHECKS = [len, str.upper, str.isdigit]


def describe(value):
    """Return call_all(CHECKS, value)."""
    return call_all(CHECKS, value)
```

## Complexity

One call per function.

## Another way

`return [f(value) for f in funcs]`.
