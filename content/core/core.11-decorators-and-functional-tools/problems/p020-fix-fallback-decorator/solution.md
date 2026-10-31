## Approach

Rewrite each decoration without `@` and follow one good call and one bad call.

1. **`@fallback` without brackets.** `fallback` is a factory: it expects the default value and returns a
   decorator. `@fallback` runs `fallback(parse_price)`, so `default` becomes the function and the name
   `parse_price` now holds `decorate`. Calling `parse_price("Rs 12.50")` runs `decorate("Rs 12.50")`, which
   returns a wrapper function, not a price. Fix: `@fallback(0.0)`.
2. **Missing `return`.** The wrapper calls `func(*args, **kwargs)` but drops the result, so a good call
   returns `None`. Fix: `return func(*args, **kwargs)`.
3. **No `functools.wraps`.** The wrapper's name is `wrapper` and the docstring is lost. Fix: `@wraps(func)`
   on the wrapper.

## Code

```python
from functools import wraps


def fallback(default):
    """If the function raises ValueError, return `default` instead."""
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError:
                return default
        return wrapper
    return decorate


@fallback(0.0)
def parse_price(text):
    """Turn a price like 'Rs 12.50' into a float."""
    return float(text.replace("Rs", "").strip())
```

## Complexity

O(1) extra per call.

## Another way

Some libraries let one decorator work both with and without brackets: if the first argument is callable,
treat it as the function. That hides this bug, but it also makes the decorator harder to read. A clear
rule is better: a factory is always called, `@fallback(0.0)`.
