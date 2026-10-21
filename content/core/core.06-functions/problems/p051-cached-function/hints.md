## Hint 1

What can serve as a dict key for 'these exact arguments'? What type is `args` inside `cached`?

## Hint 2

`args` is a tuple, and a tuple of hashable values is hashable (core.05), so it can be a dict key.

## Hint 3

```
cache = {}
hits = misses = 0
def cached(*args):
    nonlocal hits, misses
    if args in cache: hits += 1
    else: misses += 1; cache[args] = func(*args)
    return cache[args]
def stats():
    return {"hits": hits, "misses": misses}
return cached, stats
```
