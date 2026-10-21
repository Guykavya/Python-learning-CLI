# Retry a flaky operation

Some operations fail now and then and succeed if you simply try again (reading a sensor, asking a
slow server). Write `retry(func, attempts=3, errors=(ValueError,))`:

- If `attempts` is less than 1, raise `ValueError("attempts must be at least 1")` without calling
  `func`.
- Call `func()` (no arguments) up to `attempts` times. Return the result of the first call that
  does not raise.
- Only exceptions whose type is in the tuple `errors` count as "flaky" and are retried. Any other
  exception propagates **immediately**, without further attempts.
- If every attempt fails, raise the exception from the **last** attempt (the same object).

Remember from section 7 that the name in `except ... as e` is deleted after the handler: keep the
exception in another variable if you need it later.

**Example**

```python
calls = []

def flaky():
    calls.append(1)
    if len(calls) < 3:
        raise ValueError(f"attempt {len(calls)} failed")
    return "data"

retry(flaky)             # 'data'  (called 3 times)
retry(lambda: 1 / 0, errors=(ZeroDivisionError,))   # raises ZeroDivisionError after 3 tries
retry(lambda: {}["x"])   # raises KeyError at once: not in errors
```
