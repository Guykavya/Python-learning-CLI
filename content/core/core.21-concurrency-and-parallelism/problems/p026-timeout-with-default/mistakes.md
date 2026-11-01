- Putting the `try/except TimeoutError` **inside** the `async with`. Inside the block the
  task sees a `CancelledError`, not a `TimeoutError`; the `TimeoutError` only appears when the
  block exits.
- Catching `asyncio.CancelledError` and returning the default. That swallows the
  cancellation, and the timeout machinery can no longer work correctly.
- `except Exception: return default`. That also hides real bugs like `ValueError`.
- `return result or default`. A real result of `0` or `""` would be replaced.
- Starting the work with `create_task` and returning the default when time is up, without
  cancelling the task. The slow call keeps running in the background.
- Using `time.sleep` or a thread timer. Inside async code the timeout must come from
  asyncio, so the loop can cancel the awaiting task.
