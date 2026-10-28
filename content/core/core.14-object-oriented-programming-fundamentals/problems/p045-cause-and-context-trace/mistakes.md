- Writing `context: None` for `b`. Using `from e` sets `__cause__`, but Python still records the
  exception being handled in `__context__`.
- Writing `context: None` for `c`. `from None` only hides the context (`__suppress_context__ = True`);
  the `IndexError` is still in `__context__`.
- Writing `suppress: False` for `c` or `d`. Any `raise ... from ...` sets it to `True`.
- Writing `context: ValueError` for `f`. The `except` block had finished, so nothing was being
  handled when `ConfigError("after")` was raised.
- Thinking the typo in `e` is a `SyntaxError`. Using an unknown name is only noticed when the line
  runs: `NameError`.
- Following `__context__` in `g` and adding extra names. The loop follows `__cause__` only.
