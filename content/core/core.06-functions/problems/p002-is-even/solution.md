## Approach

A number is even when dividing by 2 leaves no remainder: `n % 2 == 0`. That comparison is
already a bool, so return it directly. Python's `%` gives a result with the sign of the
divisor, so `-3 % 2` is `1` and negative numbers need no special case.

## Code

```python
def is_even(n):
    """Return True if n is even, otherwise False."""
    return n % 2 == 0
```

## Complexity

O(1).

## Another way

`return not n % 2` also works, because `0` is falsy. It is shorter but less obvious to a reader;
the explicit comparison says what you mean.
