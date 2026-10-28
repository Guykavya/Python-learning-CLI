## Hint 1

Three questions: where is the dict created so each function gets its own? How do you build the
key in each of the two modes? How do you tell "not in the cache yet" apart from "in the cache
with the value `None`"?

## Hint 2

Create `cache = {}` inside `decorator`. Build `k` with an `if key is None:` branch. Use
`if k in cache: return cache[k]`. Store only after `func(...)` returned, so an exception skips
the store. Attach `wrapper.cache = cache` and a small `cache_clear` function before returning.

## Hint 3

```
decorator(func):
    cache = {}
    @wraps(func)
    wrapper(*args, **kwargs):
        k = (args, tuple(sorted(kwargs.items()))) if key is None else key(*args, **kwargs)
        if k in cache: return cache[k]
        result = func(*args, **kwargs)
        cache[k] = result
        return result
    wrapper.cache = cache
    wrapper.cache_clear = a function that calls cache.clear()
    return wrapper
```
