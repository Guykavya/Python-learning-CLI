- Retrying 4xx. A 404 or 401 will be the same next time; you just triple the load and the wait.
- Off by one: `range(retries)` gives only `retries` attempts in total, not `retries` retries.
- Sleeping after the last failure. The caller waits 0.4 s (or 40 s in production) for nothing.
- Calling `asyncio.sleep(...)` (or worse, `time.sleep`) instead of the `sleep` parameter. The
  tests cannot see the delays, and `time.sleep` would block the whole event loop.
- Catching `Exception`. A `ValueError` from a bug in your own code is then retried and finally
  hidden behind a misleading network error.
- Raising a new `RuntimeError("failed after retries")`. The caller loses the status code and the
  original traceback. Re-raise the last real error with a bare `raise`.
- Using `delay = base_delay * attempt` (linear: 0, 0.1, 0.2). The first retry would not wait at
  all; backoff doubles: `base_delay * 2**attempt`.
