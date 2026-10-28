## Hint 1

A dict key must be hashable. What do you build from `args` (already a tuple) and `kwargs` (a dict, not hashable) so that the order of the keywords does not change the key? Which function gives the items in a fixed order?

## Hint 2

`key = (args, tuple(sorted(kwargs.items())))`. Putting `key in self.cache` inside a `try` makes Python raise `TypeError` for an unhashable argument (hashing the key happens there); catch it and call the function directly. Test `key in self.cache`, **not** `self.cache.get(key)`: a cached `None` or `0` is a valid result.

## Hint 3

```
__call__(*args, **kwargs):
    key = (args, tuple(sorted(kwargs.items())))
    try:
        if key in cache: hits += 1 ; return cache[key]
    except TypeError: uncached += 1 ; return func(*args, **kwargs)
    misses += 1 ; result = func(*args, **kwargs) ; cache[key] = result ; return result
```
