## Approach

The tuple `args` is the natural key: equal arguments give equal, hashable tuples. The cache dict
and the two counters live in `make_cached`'s scope; `cached` rebinds the counters (so it needs
`nonlocal`) and mutates the dict (which needs nothing). `stats` builds a fresh dict on each call
so outsiders cannot tamper with the counters. Membership is tested with `in`, so falsy results
such as `0` and `None` are cached properly.

## Code

```python
def make_cached(func):
    """Return (cached, stats): cached(*args) memoises func; stats() gives hits and misses."""
    cache = {}
    hits = 0
    misses = 0

    def cached(*args):
        nonlocal hits, misses
        if args in cache:
            hits += 1
        else:
            misses += 1
            cache[args] = func(*args)
        return cache[args]

    def stats():
        return {"hits": hits, "misses": misses}

    return cached, stats
```

## Complexity

O(1) average per call after the first for each distinct argument tuple; O(k) memory for k distinct tuples.

## Another way

`functools.cache` and `functools.lru_cache` provide this ready-made (and `lru_cache` reports
hits and misses with `cache_info()`). Writing it yourself shows they are just a dict in a closure.
