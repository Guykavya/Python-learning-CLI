- Thinking `from None` sets `__context__` to `None`. It only sets `__cause__` and the suppress
  flag; the context is still recorded.
- Thinking `__suppress_context__` is `True` only for `from None`. Any `raise ... from ...` sets it.
- Forgetting that `raise X from e` inside `except` sets **both** `__cause__` and `__context__`
  (to the same object here).
- Expecting a bare `raise` to chain the exception to itself. It re-raises the same object
  unchanged.
- Expecting `cause_only` to have a context. Nothing was being handled, so `__context__` is
  `None` even though `__cause__` is set.
