- `except Exception:` for everything. It also swallows real bugs (a `KeyError` from somewhere
  else) and logs them as "cannot divide".
- `logger.error(...)` instead of `logger.exception(...)`. Same level, but no traceback, so the
  reader cannot see where the `TypeError` came from.
- Calling `logger.exception` outside the `except` block. There is no "current exception" there,
  so the traceback part is `NoneType: None`.
- f-strings in log calls. The message is built even when the level is off, and the template is
  lost.
- `%s` instead of `%r`. Then `"7"` and `7` look the same in the log, which hides the exact bug
  you are logging.
- Counting pairs from 1, or forgetting the index entirely: the reader cannot find the bad row.
