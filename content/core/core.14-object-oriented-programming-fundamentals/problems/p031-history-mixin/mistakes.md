- `_history = []` in the mixin's class body. Every counter and text box then writes into the same
  list, so each object shows everybody's actions.
- Adding `def __init__(self): self._history = []` to the mixin. `Counter.__init__` replaces it and
  never calls it, so `_history` never exists and `_log` crashes.
- `history()` that does `return self._history`. It crashes before the first action, and it hands
  out the real list, which the caller can then change.
- Dropping the **newest** entry when the log is too long. The log must keep the newest ones.
- Writing `str(arg)` instead of `repr(arg)`. Then `type('hi')` is logged as `type(hi)`.
- Logging in `increment` before checking or changing anything, then failing. Log after the change
  succeeds.
