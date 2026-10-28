# A memoize decorator as a callable class

**Memoizing** means remembering the result of a call so the same call is never computed twice.
Write `Memoize` in `solution.py`, used as `@Memoize` above a function.

- `Memoize(func)` wraps `func`. The attributes: `cache` (a dict), `hits`, `misses` and `uncached`
  (all start at 0).
- A call `m(*args, **kwargs)` builds a key from the arguments. **Keyword order must not matter**:
  `f(a=1, b=2)` and `f(b=2, a=1)` are one call. Positional and keyword forms are different keys.
- If the key is in `cache`: add 1 to `hits` and return the stored result.
- Otherwise: call the function, store the result, add 1 to `misses`, return it. If the function
  raises, nothing is stored and the exception propagates (the call still counts as a miss; add it
  before the call).
- If an argument is **unhashable** (a list, a dict), the key cannot be used in a dict (`TypeError`).
  Then call the function directly, without caching, and add 1 to `uncached` (not to `hits` or
  `misses`).
- Results that are falsy (`0`, `None`, `""`) are cached like any other.
- `cache_clear()` empties the cache and resets the three counters.
- Keep the function's `__name__` and `__doc__` (`functools.update_wrapper`).

**Example**

```python
@Memoize
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(80)            # 23416728348467685, instantly
fib.misses         # 81
fib.cache_clear()
```
