- Thinking only the first matching clause runs, as with `except`. With `except*` every clause that
  still has matching leaves runs once.
- Forgetting the nested `ValueError("bad zip")`. Matching looks at leaves at every depth.
- Writing `V: io ...` or a flat list. The matched part keeps the outer message `batch` and the
  nesting.
- Expecting `D: ['db down']`. `DbError` was already taken by `except* AppError`.
- Printing `end of run`. The unhandled `KeyError` and `TypeError` are re-raised at the end of the
  `try` statement, so the line after it never runs.
- Writing `['id']` instead of `["'id'"]`. `str()` of a `KeyError` adds quotes around the key.
- In part 2, writing `NetError` for the type. `except*` always gives you a group.
- In part 3, thinking the `TypeError` clause is skipped because the first clause raised, or that
  `finally` comes after `outer:`.
- In part 4, printing `else`. `else` runs only when nothing was raised at all.
