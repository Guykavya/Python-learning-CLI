- Checking `if callable(func)` but forgetting the `None` case, so `@debug()` returns `None` and
  the decorated name becomes `None`.
- Letting `prefix` be positional: `def debug(func=None, prefix="DEBUG", ...)`. Then
  `@debug("TRACE")` treats `"TRACE"` as the function and fails with a confusing error at call time.
- Calling `print` directly instead of the `log` list when `log` is given.
- Writing `if log:` to choose. An empty list is falsy, so the first line is printed instead of
  stored.
- Forgetting `wraps` in one of the two paths. Both paths should go through the same `decorator`.
