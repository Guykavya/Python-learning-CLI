- Putting `warned = False` inside `deprecated`. All functions decorated by the same
  `deprecated(...)` result share one flag, so only the first one ever warns.
- Putting `warned = False` inside `wrapper`. It is reset on every call, so it warns every time.
- Forgetting `nonlocal warned`. Python then treats `warned` as a new local variable in `wrapper`
  and `if not warned` raises `UnboundLocalError`.
- Warning after `func(...)` returns. A first call that raises never warns.
- Using `if log:` instead of `if log is None:`. An empty list is falsy, so the first warning is
  printed instead of appended.
