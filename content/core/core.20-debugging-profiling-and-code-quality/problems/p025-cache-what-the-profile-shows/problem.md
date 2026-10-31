# Cache what the profile shows

`starter.py` counts the ways to pay an amount with coins (each coin value can be used any number
of times, and the order does not matter, so 1+2 and 2+1 are the same way):

```python
def ways(amount, coins):
    return count(amount, tuple(coins), 0)


def count(amount, coins, i):
    if amount == 0:
        return 1
    if amount < 0 or i == len(coins):
        return 0
    return count(amount - coins[i], coins, i) + count(amount, coins, i + 1)
```

`ways(60, [1, 2, 5, 10, 20, 50])` is 793, and `cProfile.run('ways(60, [1, 2, 5, 10, 20, 50])', sort='tottime')` prints (real run, Python
3.14; the seconds are machine-specific, the call counts are not):

```text
         123792 function calls (48984 primitive calls) in 0.042 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  74809/1    0.036    0.000    0.042    0.042 solution.py:6(count)
    48979    0.005    0.000    0.005    0.000 {built-in method builtins.len}
        1    0.000    0.000    0.042    0.042 {built-in method builtins.exec}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.042    0.042 solution.py:1(ways)
        1    0.000    0.000    0.042    0.042 <string>:1(<module>)
```

There are only 61 possible amounts (0 to 60) and 7 possible values of `i`, so at most a few
hundred **different** questions exist. `count` is asked the same questions over and over.
`ways(500, ...)` with eight coins would take hours this way.

Make it fast by **caching** in `solution.py`:

- Decorate `count` with `functools.cache` (or `functools.lru_cache`). The tests check that
  `count` has a `cache_info()` method.
- `ways(amount, coins)` must still accept `coins` as a **list**.
- The answer must be right when `ways` is called with different coin lists one after the other.
- The tests run your code under `cProfile` and count calls: `ways(60, [1, 2, 5, 10, 20, 50])`
  must run the Python functions in `solution.py` at most 1,281 times in total (3 × 61 × 7).

**Example**

```python
ways(4, [1, 2])                            # 3: 1+1+1+1, 1+1+2, 2+2
ways(0, [5])                               # 1: pay nothing
ways(200, [1, 2, 5, 10, 20, 50, 100, 200]) # 73682
ways(500, [1, 2, 5, 10, 20, 50, 100, 200]) # 6295434, instantly
count.cache_info()                         # CacheInfo(hits=..., misses=..., maxsize=None, currsize=...)
```
