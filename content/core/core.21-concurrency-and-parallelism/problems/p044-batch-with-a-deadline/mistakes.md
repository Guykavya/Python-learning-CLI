- `for t in pending: t.cancel()` and return. The cancellations have been requested but not
  delivered; the `finally` blocks run later (or never, if the loop closes first). The test
  sees no `cleaned up` line.
- `await asyncio.sleep(timeout)` and then checking `task.done()`. It always waits the full
  timeout, even when everything finished in 10 ms.
- `asyncio.wait_for(asyncio.gather(*tasks), timeout)`. On timeout everything is cancelled,
  including the finished results, and you get a `TimeoutError` instead of partial results.
- Calling `task.result()` on a failed task. It **raises** the task's exception; use
  `task.exception()` first.
- Calling `asyncio.wait([])` for an empty list: `ValueError`.
- Building results from `done` (a set). Sets have no order; walk the original `tasks` list.
- `await asyncio.gather(*pending)` without `return_exceptions=True`. It raises the first
  `CancelledError` and your function ends up cancelled itself.
