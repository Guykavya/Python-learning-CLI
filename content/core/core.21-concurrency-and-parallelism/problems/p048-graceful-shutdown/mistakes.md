- Cancelling the tasks and returning. `cancel()` only requests a stop; cleanup that awaits has
  not run yet, and the program may exit (or close the loop) before it does.
- `await asyncio.gather(*tasks)` without `return_exceptions=True`. It raises the first
  `CancelledError` (or the crash) and `stop()` itself fails half-way.
- `except asyncio.CancelledError: pass` inside the worker loop. The worker swallows the
  cancellation, keeps looping, and `stop()` waits forever.
- Filtering with `isinstance(o, BaseException)`. That includes the `CancelledError`s of the
  workers you stopped on purpose; only `Exception`s are crashes.
- Not keeping references to the tasks (`asyncio.create_task(...)` with the result thrown
  away). You cannot stop them later, and the loop may even garbage-collect them mid-run.
- Leaving `self._tasks` filled after stopping. A second `stop()` gathers them again, `running`
  stays `True`, and `start()` refuses to restart.
- Making `start` `async def` and forgetting to await it: the workers are never created.
- Returning `True` from `__aexit__`: it would swallow the body's exception.
