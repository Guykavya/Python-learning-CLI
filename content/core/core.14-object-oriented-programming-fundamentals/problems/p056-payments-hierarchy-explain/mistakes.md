- One class per error with no grouping. The caller then needs a long `except (A, B, C, D)` list and
  must update it in every release.
- Grouping by where the code lives (`ValidationModuleError`, `NetworkModuleError`) instead of what
  the caller should do.
- Putting important data only into the message. Callers start parsing `str(e)`, and the next wording
  change breaks them.
- Re-raising without `from` (or with `from None`) everywhere. The traceback loses the real reason,
  for example which socket call timed out.
- Putting `except PaykitError` before the specific clauses. The first matching clause wins, so the
  specific ones never run.
- Raising plain built-in exceptions (`ValueError`, `RuntimeError`) from the library. They escape
  `except PaykitError`.
