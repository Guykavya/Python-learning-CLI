- Counting 15 calls for `fib_a(5)`. That is the number without a cache; here hits stop the
  recursion early.
- Expecting `fib_a.calls` to be 6. The counter is outside the cache, so cache hits are counted too.
- Expecting the second `fib_b(5)` to make the count 7. It is a hit, answered by the cache above
  the counter.
- Expecting `counted_plain.calls` to be 15. The recursive calls go to `plain`, not to `counted_plain`.
- Expecting `fib_b.calls` to be 6. `wraps` copied the attribute's value once; it is not a link.
- Writing `wrapper` as the name of `fib_b`. Both `counted` and `lru_cache` copy `__name__`.
