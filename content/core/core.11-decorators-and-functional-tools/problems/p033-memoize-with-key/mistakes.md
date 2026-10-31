- `if cache.get(k):` or `if cache.get(k) is not None:`. A stored `None`, `0` or `""` is then
  computed again on every call.
- `tuple(kwargs.items())` without sorting. Then `f(a=1, b=2)` and `f(b=2, a=1)` are different keys.
- Creating `cache = {}` in `memoize` instead of `decorator`. Two functions decorated by the same
  `memoize()` result then share a cache and can return each other's answers.
- `def cache_clear(): cache = {}`. That makes a new local dict and leaves the real cache full.
- Catching `TypeError` for unhashable keys and silently calling the function. It hides that the
  cache never works for those calls.
- Storing the result before calling, for example `cache[k] = None` as a "placeholder". A failed
  call then leaves a wrong `None` in the cache.
