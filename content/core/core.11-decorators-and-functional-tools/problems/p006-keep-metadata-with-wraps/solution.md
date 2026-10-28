## Approach

`wraps(func)` returns a decorator that copies `__name__`, `__qualname__`, `__doc__`, `__module__` and the
attribute dict from `func` onto the function it decorates, and sets `__wrapped__ = func`. Put it on the
wrapper. The wrapper's behaviour does not change; only its labels do.

## Code

```python
from functools import wraps


def strip_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).strip()
    return wrapper
```

## Complexity

O(1) extra at decoration time. Each call costs the original call plus the strip.

## Another way

You could copy by hand: `wrapper.__name__ = func.__name__` and `wrapper.__doc__ = func.__doc__`. It is
easy to forget a field (`__qualname__`, `__module__`, `__wrapped__`), so always use `wraps`. Make it a
habit: every wrapper you write gets `@wraps(func)`.
