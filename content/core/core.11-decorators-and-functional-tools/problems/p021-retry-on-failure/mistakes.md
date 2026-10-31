- Counting retries instead of attempts: `for _ in range(attempts + 1)` makes one call too many.
- Sleeping after the last failure. The caller waits for nothing before getting the error.
- `raise Exception("failed")` after the loop. The caller loses the real exception type and message.
  Use a bare `raise` inside the `except` block.
- `except Exception:` instead of `except exceptions:`. Then a `ValueError` from a bug is retried,
  which hides the bug and wastes time.
- Checking `attempts < 1` inside `wrapper`. Then `retry(0)` does not fail until the first call.
- Calling `time.sleep` directly instead of the `sleep` parameter. The tests cannot replace it and
  would really wait.
