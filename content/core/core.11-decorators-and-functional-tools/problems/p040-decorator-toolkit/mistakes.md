- Putting the per-function state (`store`, `recent`) in the factory instead of in `decorator`.
  Two functions decorated with the same `cache()` result then share answers.
- `timer` that appends only after a normal return. Slow calls that fail are the ones you most
  want to measure. Use `finally`.
- `retry` that sleeps `delay` every time, or multiplies before the first sleep, so the waits are
  `2, 4` instead of `1, 2`.
- `retry` that sleeps after the last attempt or raises a new generic exception instead of the
  real one.
- `cache` that checks `if store.get(key):`. A cached `None`, `0` or `""` is then computed again.
- `cache` that refreshes the stored time on every hit. Then an entry read often never expires,
  and stale data lives for ever.
- `cache` LRU that evicts the oldest **stored** entry instead of the least recently **used**:
  forgetting to move a hit to the end of the dict.
- `cache_clear` that writes `store = {}`. That only rebinds a local name; the wrapper still
  uses the old dict. Use `store.clear()`.
- `rate_limit` that records the time of blocked calls. Then a client that keeps trying is
  blocked for ever.
- `rate_limit` that uses `<=` in `now - t <= period`, so a call still counts at exactly `t + period`.
- `recent = [t for t in recent if ...]` inside `wrapper`. Assigning makes `recent` a local name and
  raises `UnboundLocalError`. Use `recent[:] = ...` or `nonlocal recent`.
- Calling `time.sleep` or `time.monotonic` directly instead of the `sleep` and `clock` parameters.
  The tests cannot control them, and they would really wait.
- Forgetting `wraps` in one layer. Every layer above it then shows the name `wrapper`.
