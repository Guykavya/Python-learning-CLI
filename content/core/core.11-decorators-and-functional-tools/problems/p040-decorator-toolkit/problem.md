# Project: a decorator toolkit

Build five decorators that real programs use every day, then stack them. Put them all in
`solution.py`. Every one of them:

- is a **decorator factory** (it takes settings and returns a decorator), used with parentheses,
  for example `@cache()` or `@retry(attempts=3)`;
- uses `functools.wraps`, so the name, docstring and `__wrapped__` are kept;
- passes all positional and keyword arguments through to the function;
- takes anything slow or changing (the clock, sleeping) as a parameter, so the tests can give
  it a **fake** clock and never really wait. The defaults are the real ones from `time`.

Check bad settings when the factory is called (before any function is decorated) and raise
`ValueError`.

---

## 1. `timer(log, clock=time.perf_counter)`

After each call, append `(name, elapsed)` to the list `log`, where `elapsed` is
`clock()` after the call minus `clock()` before it. Record it **even if the call raises**
(and let the exception continue).

## 2. `retry(attempts=3, exceptions=(Exception,), delay=0.1, backoff=2.0, sleep=time.sleep)`

- Make at most `attempts` calls in total.
- After a failed attempt that will be retried, call `sleep(wait)`. The first wait is `delay`;
  each next wait is the previous one times `backoff`. With `delay=1, backoff=2` the waits are
  `1, 2, 4, ...`. This is called **exponential backoff**: it gives a busy server more and more
  time to recover.
- Do not sleep after the last attempt. If it fails, re-raise its exception.
- An exception that does not match `exceptions` is raised at once (no retry, no sleep).
- `ValueError` if `attempts < 1`, `delay < 0`, or `backoff < 1`.

## 3. `cache(maxsize=None, ttl=None, clock=time.monotonic)`

- The key is `(args, tuple(sorted(kwargs.items())))`. A `None` result is cached too. A call that
  raises stores nothing.
- `maxsize`: keep at most this many entries. When a new entry makes it one too many, remove the
  **least recently used** one (a hit counts as a use). `None` means no limit.
- `ttl` ("time to live", in seconds): an entry stored at time `t` is fresh while
  `clock() - t < ttl`. Reading an entry does **not** refresh its time. An expired entry counts as
  a miss: compute again and replace it. `None` means entries never expire.
- `f.cache_info()` returns `{"hits": h, "misses": m, "size": number of stored entries}`.
- `f.cache_clear()` removes all entries and sets the counters back to 0.
- `ValueError` if `maxsize` is not `None` and below 1, or `ttl` is not `None` and not positive.

Tip: a dict remembers insertion order. If you `pop` a key and insert it again, it moves to the
end. Then the first key, `next(iter(d))`, is the least recently used one.

## 4. `rate_limit(calls, period, clock=time.monotonic)`

- Allow at most `calls` calls in any window of `period` seconds. A call made at time `t` counts
  until time `t + period`; at exactly `t + period` it no longer counts.
- A call that would go over the limit does **not** run the function and raises `RuntimeError`
  with a clear message that contains `rate limit` and the function name, for example:
  `rate limit exceeded for ping: at most 2 calls per 10s, try again in 1.00s`.
- Blocked calls are not recorded (they do not use up the limit).
- Each decorated function has its own limit.
- `ValueError` if `calls < 1` or `period <= 0`.

## 5. `logger(log)`

- Before the call append `("call", name, args, kwargs)` (`args` is the tuple, `kwargs` the dict).
- After a normal return append `("return", name, result)`.
- If the call raises, append `("raise", name, exception class name)` and re-raise.

---

## Example

```python
log = []
waits = []

@logger(log)
@retry(attempts=3, exceptions=(ConnectionError,), delay=1, backoff=2, sleep=waits.append)
@cache(maxsize=100, ttl=60)
def get_price(item):
    ...   # talks to a server; fails with ConnectionError twice, then returns 42

get_price("pen")    # 42
waits               # [1, 2]
log                 # [("call", "get_price", ("pen",), {}), ("return", "get_price", 42)]
get_price("pen")    # 42 from the cache: the server is not asked again
get_price.__name__  # "get_price"
```

## Stacking: order matters

The tests also stack your decorators and check the effect of the order:

- `logger` **outside** `retry` sees one call; `retry` outside `logger` logs every attempt.
- `cache` outside `rate_limit`: cache hits never reach the limiter, so they do not use up calls.
- `timer` outside `cache`: a hit takes no (fake) time, because the body does not run.
- A stack of all five still has the original name and docstring.

Remember: the decorator **closest to `def`** is applied first and runs **innermost** at call time.
