## Approach

- The dict lives in `decorator`, which runs once per decorated function, so caches are separate.
- The default key is a tuple of the positional arguments and the **sorted** keyword items, so
  the order of keywords does not matter. A tuple is hashable only if everything inside it is,
  so a list argument raises `TypeError` when the dict looks up the key.
- `k in cache` checks for the key, not for a truthy value, so `None` results are cached.
- The result is stored only after the call returned. If the call raises, the line that stores is
  never reached.
- `cache_clear` uses `cache.clear()`, which empties the **same** dict that `wrapper.cache`
  points to. Writing `cache = {}` inside it would only create a new local variable.

## Code

```python
from functools import wraps


def memoize(key=None):
    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            if key is None:
                k = (args, tuple(sorted(kwargs.items())))
            else:
                k = key(*args, **kwargs)
            if k in cache:
                return cache[k]
            result = func(*args, **kwargs)
            cache[k] = result
            return result

        def cache_clear():
            cache.clear()

        wrapper.cache = cache
        wrapper.cache_clear = cache_clear
        return wrapper
    return decorator
```

## Complexity

O(1) average per call for the dict, plus building the key: O(a + k log k) for a positional and
k keyword arguments. Memory grows with every new key; there is no size limit.

## Another way

`functools.lru_cache` plus a front-door function that converts lists to tuples. That gives you a
size limit and statistics for free, but less control over the key. Normalising positional and
keyword calls to one key needs `inspect.signature(func).bind(...)` and `apply_defaults()`:
then `area(2, 3)`, `area(2, h=3)` and `area(w=2, h=3)` all become the same key.
