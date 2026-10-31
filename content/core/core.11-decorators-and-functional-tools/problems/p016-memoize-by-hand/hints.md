## Hint 1

Where must the dict be created so each decorated function gets its own, and it survives between calls?
(Inside `memoize`, outside `wrapper`.)

## Hint 2

A dict key must be hashable. `args` is a tuple already. `kwargs` is a dict, which is not hashable. How can
you turn it into a tuple whose order is always the same?

## Hint 3

```
cache = {}
wrapper(*args, **kwargs):
    key = (args, tuple(sorted(kwargs.items())))
    if key not in cache:
        cache[key] = func(*args, **kwargs)
    return cache[key]
wrapper.cache = cache
```
