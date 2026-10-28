# memoize(key=...): a cache you control

`lru_cache` builds its keys for you, and it rejects lists. Here you write a cache where the
caller can choose how the key is made.

Write a decorator factory `memoize(key=None)` in `solution.py`. It is always used with
parentheses: `@memoize()` or `@memoize(key=...)`.

1. **Default key**: `(args, tuple(sorted(kwargs.items())))`. Sorting the keyword items means
   `f(a=1, b=2)` and `f(b=2, a=1)` share one entry.
2. **Custom key**: if `key` is given, the cache key is `key(*args, **kwargs)`. This lets you
   cache functions that take lists (`key=lambda xs: tuple(xs)`) or treat `"Ann"` and `"ANN"` as
   the same (`key=str.lower`).
3. The cache is a dict stored as the attribute `cache` on the wrapper (`f.cache`), and
   `f.cache_clear()` empties it.
4. A result of `None` (or `0`, or `""`) is a real result and **must be cached** too.
5. If the function raises, nothing is stored; the next call tries again.
6. Each decorated function has its own cache, even when two functions are decorated with the
   same `memoize()` result.
7. With the default key, an unhashable argument such as a list raises `TypeError`. That is fine,
   just do not hide it.
8. Use `functools.wraps`.

**Example**

```python
@memoize()
def area(w, h=1):
    print("computing")
    return w * h

area(2, h=3)     # prints computing, returns 6
area(2, h=3)     # 6, no print
len(area.cache)  # 1

@memoize(key=lambda xs: tuple(xs))
def total(xs):
    return sum(xs)

total([1, 2])    # 3  (a list works, because the key is a tuple)
```

Note: with the default key, `area(2, 3)` and `area(2, h=3)` are **different** keys. The key does
not know parameter names. This is the same as `lru_cache`.
