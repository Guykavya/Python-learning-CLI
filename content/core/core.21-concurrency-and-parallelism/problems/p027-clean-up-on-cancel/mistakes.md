- Releasing after the `await` with no `finally`. Any exception or cancel skips the line.
- `except asyncio.CancelledError: return None` (or `pass`). The task then ends "successfully",
  and timeouts, task groups and shutdown code that rely on the cancel break.
- `except Exception:` for cleanup. `CancelledError` is a `BaseException`, not an `Exception`
  (since Python 3.8), so that handler does not run on cancel.
- Putting `conn = await pool.acquire()` **inside** the `try`. A cancel during acquire then
  reaches `finally`, where `conn` does not exist (`UnboundLocalError`) or a wrong value is
  released.
- Releasing in both an `except` and the `finally`, so the connection is released twice.
