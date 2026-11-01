- Cleanup lines after a bare `yield` (the starter). They are skipped when the body raises or
  the task is cancelled.
- `except Exception: pass` around the `yield`. The error is swallowed, and
  `@asynccontextmanager` then continues as if the body succeeded.
- `except Exception:` plus cleanup, without `finally`. A cancel (`CancelledError` is a
  `BaseException`) skips it.
- Putting `log.append("open")` inside the `try`. If opening failed, the `finally` would
  "close" something that was never opened.
- Creating the state dict at module level. Two sessions would share one dict.
- Using `@contextmanager` with a plain `def`. A plain generator cannot `await`, and plain
  `with` cannot be used with an async context manager.
