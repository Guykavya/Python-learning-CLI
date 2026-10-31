## Approach

The cache lives in the closure of `memoize`, so it is created once per decorated function and kept between
calls. The key combines the positional tuple with the sorted keyword items, so keyword order does not
matter. Testing `key not in cache` (not `.get`) keeps a stored `None` as a hit. If `func` raises, the
assignment never happens, so nothing is stored. `wrapper.cache = cache` exposes the same dict object.

## Code

```python
from functools import wraps


def memoize(func):
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    return wrapper
```

## Complexity

A hit costs O(k log k) to build the key for k keyword arguments, plus an O(1) dict lookup. The cache keeps
one entry per distinct call, so memory grows with the number of distinct arguments.

## Another way

`functools.cache` (or `lru_cache(maxsize=None)`) does this for you, faster, and adds `cache_info()`. One
difference: it treats `f(1)` and `f(x=1)` as different keys too, just like ours.
