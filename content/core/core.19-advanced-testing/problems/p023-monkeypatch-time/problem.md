# Testing time: monkeypatching

Sometimes you cannot add a `clock` parameter (old code, a decorator, a third-party call). Then you
**replace the time source during the test** with `monkeypatch.setattr`. The trick is to give the code
one small, patchable place that reads the time.

In `solution.py` write:

```python
import time

def now(): ...                  # returns time.monotonic()  (call it through the module: time.monotonic())

class RateLimiter:
    def __init__(self, limit, per_seconds): ...
    def allow(self): ...        # True if another call is allowed right now, else False
```

`RateLimiter(3, 10)` allows at most 3 calls in any window of 10 seconds. A call made at time `t`
counts against the limit until `now - t >= per_seconds` (the border frees the slot). Only allowed
calls count. `allow()` reads the time **once**, by calling the module-level function `now()` (not
`time.monotonic` directly). `limit < 1` or `per_seconds <= 0` raises `ValueError`.

The checker patches `solution.now` in some tests and `time.monotonic` in others; both must work, which
means `now()` must call `time.monotonic()` through the `time` module (not `from time import monotonic`).

**Example**

```python
limiter = RateLimiter(2, 10)
limiter.allow()   # True   (at t=0)
limiter.allow()   # True
limiter.allow()   # False  (still t=0)
# ... 10 seconds later: allow() -> True
```
