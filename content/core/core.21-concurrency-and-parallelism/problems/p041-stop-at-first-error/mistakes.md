- Using `with ThreadPoolExecutor() as ex:` and `break` out of the loop, expecting the rest to
  stop. The `with` exit calls `shutdown(wait=True)` with `cancel_futures=False`, so every queued
  function still runs. Cancel them first.
- Using `executor.map`. It raises the first error only when iteration reaches that item **in
  input order**, possibly long after it happened, and it does not cancel the rest.
- Calling `future.result()` to check for errors inside the loop without `try`. It raises the
  function's exception in your thread; then you need a `try` anyway.
- Calling `.result()` or `.exception()` on a cancelled future while collecting. Both raise
  `CancelledError`; check `future.cancelled()` first.
- Building `results` in completion order (appending inside the `as_completed` loop). The
  caller asked for input order.
- Returning before the running functions finish (`shutdown(wait=False)`). They keep running
  after the caller thinks the migration has stopped.
- Raising the error instead of returning it. The caller asked for a `(results, error)` pair so
  it can report the partial progress too.
