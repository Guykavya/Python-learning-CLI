## Approach

`fib(4)` misses and calls `fib(3)`, which calls `fib(2)`, which calls `fib(1)` and then `fib(0)`. Those
five calls are misses: `compute 4, 3, 2, 1, 0`. Back up the tree, `fib(3)` needs `fib(1)` (stored: hit)
and `fib(4)` needs `fib(2)` (stored: hit). So: hits 2, misses 5, 5 stored values. The result is 3.

`fib(5)` is new: `compute 5` (miss 6). Its two calls `fib(4)` and `fib(3)` are both stored: hits 4.

`fib(3)` is stored: no `compute` line, hits 5, result 2.

`cache_clear()` removes every stored value and resets the statistics. `fib(1)` is then a fresh miss.

## Output

```text
compute 4
compute 3
compute 2
compute 1
compute 0
3
CacheInfo(hits=2, misses=5, maxsize=None, currsize=5)
compute 5
5
CacheInfo(hits=4, misses=6, maxsize=None, currsize=6)
2
CacheInfo(hits=5, misses=6, maxsize=None, currsize=6)
compute 1
1
CacheInfo(hits=0, misses=1, maxsize=None, currsize=1)
```

## Complexity

With the cache, `fib(n)` runs its body once per value of `n`: O(n) time and O(n) memory. Without it,
the same tree has O(2^n) calls.

## Another way

`functools.cache` is the same as `lru_cache(maxsize=None)`, a little shorter to write. Use a number for
`maxsize` when the set of possible arguments is large and you want to cap memory: the least recently
used entries are then thrown out.
