## Approach

The inner function uses `factor` from the enclosing scope. Python keeps that variable alive in a cell attached to the returned function, so each multiplier remembers its own factor.

## Code

```python
def make_multiplier(factor):
    """Return a function that multiplies its argument by factor."""
    def multiply(n):
        return n * factor
    return multiply
```

## Complexity

O(1) to create, O(1) per call.

## Another way

`return lambda n: n * factor` is the same closure written as a lambda.
