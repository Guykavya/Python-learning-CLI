- Writing `now=datetime.now()` (with brackets). The clock is read once when the function is
  defined, so every call sees the same moment.
- Passing a `datetime` instead of a function, then calling `now()` on it (`TypeError`), or the
  reverse: the tests give a function.
- Calling `datetime.now()` in the body "just in case" when `now` is None. Use the default
  parameter, or `now = now or datetime.now` (a reference, not a call).
- Forgetting to close the file. Use `with opener(path, "w") as f:`; a fake that records `close`
  will notice.
- Opening the file with `open(...)` in the body and only using the injected opener for the mode.
- Changing the output format while editing: the injected version must write exactly the same
  bytes as the old one.
