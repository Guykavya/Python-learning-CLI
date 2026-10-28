# A retry decorator written as a class with arguments

Networks fail for a moment and then work again, so code often **retries**. A decorator with
arguments, `@Retry(times=3, exceptions=(OSError,))`, needs two steps: first
`Retry(times=3, ...)` creates an object (the arguments), then Python calls that object with the
function (`__call__(func)`), and it returns the wrapper. With a class, the arguments are stored on
`self` and the two steps are `__init__` and `__call__`. Write `Retry` in `solution.py`.

- `Retry(times=3, exceptions=(Exception,))`: `times` is the **total number of attempts** (so
  `times=1` means no retry). `times < 1` raises `ValueError`. `exceptions` is a tuple of exception
  classes that count as "try again".
- `Retry(...)(func)` returns a wrapper function with the same name and docstring as `func`
  (`functools.wraps`).
- The wrapper calls `func(*args, **kwargs)`. If it returns, the wrapper returns that result at once.
  If it raises an exception from `exceptions`, try again. If the **last** attempt also fails, the wrapper raises that
  last exception. An exception that is **not** in `exceptions` propagates immediately.
- The `Retry` object has an attribute `failures`: the total number of caught exceptions from
  `exceptions`, over all functions it decorates (including the last one that was re-raised).
- No waiting between attempts.

**Example**

```python
@Retry(times=3, exceptions=(ConnectionError,))
def fetch():
    ...        # fails twice with ConnectionError, then works

fetch()        # returns the result of the third attempt
```
