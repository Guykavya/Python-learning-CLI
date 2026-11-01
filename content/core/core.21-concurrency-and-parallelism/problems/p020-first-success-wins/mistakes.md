- Using `with ThreadPoolExecutor() as pool:` and `return` inside it. The block's exit waits
  for every job, so the call is as slow as the slowest mirror.
- Calling `fut.result()` on the first finished future without checking it. If that mirror
  failed, the error is raised instead of trying the others.
- Returning `fut.exception()` or the exception object as a "result".
- Passing the full `timeout` to every `wait`. Each failure restarts the clock; use a deadline.
- Treating an empty `done` set as "all failed". Empty `done` means the timeout passed.
- Forgetting to update `pending` with the second set `wait` returns, so finished futures come
  back again and again (an endless loop that keeps seeing the same failure).
- Expecting `cancel()` to stop a running thread. It only stops jobs that have not started.
- Raising `RuntimeError` without `from last_error`. The caller then cannot see why the
  mirrors failed.
