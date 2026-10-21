# A cache with hit counting

Write `make_cached(func)` that returns a **pair** `(cached, stats)`:

- `cached(*args)` returns `func(*args)`, but remembers results: if the same arguments come again,
  it returns the stored result **without calling `func`**. All arguments are hashable.
- `stats()` returns a **new** dict `{"hits": h, "misses": m}`: how many calls were answered from
  the cache, and how many had to call `func`.

Separate calls of `make_cached` have separate caches.

**Example**

```python
def slow_add(a, b):
    return a + b

add, stats = make_cached(slow_add)
add(2, 3)      # 5   (miss: slow_add is called)
add(2, 3)      # 5   (hit: slow_add is not called)
add(3, 2)      # 5   (miss: different arguments)
stats()        # {'hits': 1, 'misses': 2}
```
