- Plain `gather(...)` with a `try/except` around it. The `except` catches the first error,
  but the results of the others are gone.
- `if result:` to decide success. `0`, `None`, `""` and `[]` would land in `failed` (or
  nowhere).
- Storing the exception object or `str(exc)` in `failed`. The task asks for the type name:
  `type(exc).__name__`. (`str(KeyError(2))` is `'2'`, which says nothing.)
- Awaiting each fetch inside its own `try` in a `for` loop. Correct dicts, but no
  concurrency.
- Building `ok` from `zip(ids, results)` without checking the type, so exception objects end
  up as "results".
