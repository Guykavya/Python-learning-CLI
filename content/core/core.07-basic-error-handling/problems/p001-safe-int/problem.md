# Safe whole-number parsing

Write `to_int(text, default=0)` that converts `text` to an int with `int(text)`.

- If `text` is not a valid whole number, `int` raises `ValueError`. In that case return
  `default` instead.
- Catch **only** `ValueError`. If the caller passes something that is not text at all, such as
  `None` or a list, `int` raises `TypeError`. That is a bug in the caller's code, so let it
  propagate: do not catch it.

**Examples**

```python
to_int("42")            # 42
to_int("  -7 ")         # -7     int() ignores surrounding spaces
to_int("abc")           # 0
to_int("3.5")           # 0      not a whole number
to_int("abc", None)     # None
to_int(None)            # raises TypeError (not caught)
```

Chapter sections 5 and 6 cover this. Do not use `isdigit()`: section 14 shows why it is the
wrong check.
