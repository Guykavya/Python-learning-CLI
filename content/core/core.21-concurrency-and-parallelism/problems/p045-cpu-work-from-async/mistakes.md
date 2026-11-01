- Calling `cpu_fn(job)` directly in `async def`. The function is not async, so it blocks the
  loop; making the caller `async` does not make the work non-blocking.
- `await loop.run_in_executor(...)` inside the `for` loop. Each job is awaited before the next
  one starts: the loop stays responsive, but the jobs run one at a time.
- Writing `loop.run_in_executor(executor, cpu_fn(job))`. That calls `cpu_fn` **now**, on the
  loop thread, and passes its result as the "function". Pass the function and its argument
  separately.
- Using `asyncio.to_thread` or `run_in_executor(None, ...)` when an executor was given. The
  work runs in the default pool instead of the one the caller sized for it.
- Using a thread pool for pure-Python number crunching and expecting it to use all cores. The
  GIL lets one thread run Python bytecode at a time; use a `ProcessPoolExecutor`.
- Passing a lambda or a nested function to a `ProcessPoolExecutor`. It cannot be pickled.
