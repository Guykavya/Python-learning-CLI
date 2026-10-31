## Approach

**fib_a (counter outside).** `fib_a(5)` is one call, and the misses for n = 5, 4, 3, 2 each make
two inner calls through the name `fib_a`: 1 + 4 × 2 = **9** calls, all counted. Six of them are
misses (n = 5 .. 0) and three are hits. The second `fib_a(5)` is one more counted call (a hit):
**10**. The cache below the counter has `hits=4, misses=6`.

**fib_b (counter inside).** The same 9 + 1 calls reach the cache, but only the 6 misses go down
to the counter: **6** both times. `fib_b.cache_info()` shows the same numbers as before: 4 hits,
6 misses.

**counted_plain.** `counted(plain)` was assigned to a **new** name. The body of `plain` calls
`plain`, which is still the undecorated function. Only the outer call is counted: **1**.

**fib_b.calls.** `lru_cache` copied `counted`'s wrapper `__dict__` when it was applied, at that
moment `calls` was 0. The counter later increases `wrapper.calls` on the inner wrapper, not the
copy, so `fib_b.calls` stays **0**. The name is `fib_b`, copied down through both layers.

## Output

```text
5 9
5 10
CacheInfo(hits=4, misses=6, maxsize=None, currsize=6)
5 6
5 6
CacheInfo(hits=4, misses=6, maxsize=None, currsize=6)
5 1
fib_b 0
```

## Complexity

With the cache, O(n) calls; without it (`plain`), O(2^n) calls, but only one is counted here.

## Another way

To count **all** calls of `plain`, decorate it with `@counted` on its own `def` (so the name
`plain` is the wrapper), or rebind the name: `plain = counted(plain)`. The lesson: a decorator
only sees recursive calls if the **name used inside the body** points to the wrapper.
