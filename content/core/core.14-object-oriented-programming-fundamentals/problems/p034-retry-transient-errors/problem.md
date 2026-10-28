# Retry only the errors worth retrying

Network calls fail sometimes. Some failures are **transient** (a timeout: trying again may work),
others are **permanent** (a wrong password: trying again is pointless). A good retry helper tries
again only for transient errors, and when it finally gives up it says so, while keeping the last
real error attached. Write it in `solution.py`.

**Exception classes**

- `TransientError(Exception)`: a failure that may go away if you try again.
- `PermanentError(Exception)`: a failure that will not go away.
- `RetryExhausted(Exception)`: raised by `retry` when every attempt failed with a transient error.
  `RetryExhausted(attempts, last_error)` stores both as attributes `attempts` and `last_error`, and
  its message (what `str()` gives) is `f"gave up after {attempts} attempts"`.

**`retry(func, attempts=3, on_retry=None)`**

- `attempts` must be an `int` of at least 1, otherwise raise `ValueError` (before calling `func`).
- Call `func()` (no arguments). If it returns, return its result at once.
- If it raises a `TransientError` (or a subclass of it) and attempts are left, call it again.
  Before each new try, if `on_retry` is given, call `on_retry(number, err)`, where `number` is the
  number of the attempt that just failed (1, 2, ...) and `err` is its exception.
- Any other exception (a `PermanentError`, a `KeyError`, ...) is **not** retried: let it propagate
  unchanged.
- If the last attempt also raised a `TransientError`, raise `RetryExhausted(attempts, err)`
  **chained from** that last error with `raise ... from err`, so its `__cause__` is that error.
  `on_retry` is not called after the last attempt.

**`retrying(attempts=3)`** is a decorator factory: `@retrying(5)` above a function makes every call
of it go through `retry` with those attempts. Pass the call's arguments through, and keep the
function's name with `functools.wraps`.

**Example**

```python
calls = []
def fetch():
    calls.append(1)
    if len(calls) < 3:
        raise TransientError("timeout")
    return "data"

retry(fetch, attempts=3)     # 'data'  (failed twice, worked on the 3rd call)

def login():
    raise PermanentError("wrong password")
retry(login)                  # PermanentError: wrong password   (called once only)

def always_down():
    raise TransientError("server down")
retry(always_down, attempts=2)
# RetryExhausted: gave up after 2 attempts
# (its __cause__ is the TransientError('server down') from the 2nd call)

@retrying(4)
def add(a, b):
    return a + b
add(2, b=3)                   # 5
add.__name__                  # 'add'
```
