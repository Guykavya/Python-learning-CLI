## Approach

The division is the only operation and the only expected failure is a zero divisor, which raises
`ZeroDivisionError` for both `0` and `0.0`. Catch exactly that type.

## Code

```python
def safe_divide(a, b):
    """Return a / b, or None if b is zero."""
    try:
        return a / b
    except ZeroDivisionError:
        return None
```

## Complexity

O(1).

## Another way

LBYL: `if b == 0: return None` then `return a / b`. For plain numbers this is just as correct and
equally clear; the problem asks for EAFP for practice. `except ArithmeticError` would also work but
is wider than needed: it also catches `OverflowError`, which this function does not plan for.
