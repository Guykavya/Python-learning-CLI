- Retrying every 4xx. A 404 or 401 will fail the same way next time; you multiply the load and
  hide the real problem behind a long wait.
- Forgetting 429. It is a 4xx code, but it means "too fast, try later", which is the most
  common reason to retry against a public API.
- Ignoring `Retry-After`, or adding jitter to it. The server told you exactly when it will accept
  you again; retrying earlier gets another 429 and can get your key blocked.
- Crashing on `int("Wed, 21 Oct ...")`. A malformed header must not turn a retryable error
  into a `ValueError`.
- Calling `time.sleep` or `random.random` directly. Tests cannot see or control them, and a test
  suite with real backoff takes minutes.
- Sleeping after the last attempt, or making `max_attempts + 1` requests (`range(max_attempts + 1)`
  when the parameter counts attempts, not retries).
- Catching `Exception`. A `KeyError` in your own code would be retried four times and finally
  reported as if the network had failed.
- Raising a new `RuntimeError("gave up")`. The caller loses the status code and the original
  traceback; re-raise the last real error with a bare `raise`.
- Not capping the backoff: with `base_delay * 2**(k-1)` the 10th retry would wait 512 seconds.
