- Writing `raise ConfigError(...)` without `from e` inside the `except`. The cause is lost (it only
  appears as `__context__`, and the traceback says "during handling" instead of "direct cause").
- Raising the range error inside the `except` block, or wrapping it in a `try` that catches it again.
- Catching `Exception` around `parse_port(...)` in `load_port`. Every parse error then turns into
  "missing setting: port".
- Forgetting `.strip()`. Python's `int(" 8080 ")` happens to allow spaces, but be explicit.
- Using `{text}` instead of `{text!r}`. The message must show the quotes: `got 'eighty'`.
