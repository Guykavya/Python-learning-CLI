## Approach

Two ideas combine. A closure with `nonlocal` keeps a private count per wrapper. `*args, **kwargs`
in the wrapper's definition, and `func(*args, **kwargs)` in its body, forward any arguments
unchanged. Check the limit **before** calling, so `func` never runs once the limit is reached.

## Code

```python
def limit_calls(func, max_calls):
    """Return a wrapper that forwards its arguments to func for the first max_calls calls, then returns None."""
    used = 0

    def wrapper(*args, **kwargs):
        nonlocal used
        if used >= max_calls:
            return None
        used += 1
        return func(*args, **kwargs)

    return wrapper
```

## Complexity

O(1) overhead per call.

## Another way

Count down instead: `remaining = max_calls`, and refuse when `remaining == 0`. This wrapper
pattern is exactly what a **decorator** is; a later module shows the `@` syntax for applying it.
