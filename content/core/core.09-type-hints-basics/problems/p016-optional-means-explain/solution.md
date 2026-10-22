See the model answer shown when you check. The ideas that must appear:

1. `Optional[str]` is the old spelling of `str | None`: a `str` or `None`. It describes a **value**, not a parameter.
2. Meera is wrong. Only a **default value** lets an argument be omitted. `send_b("hi")` and `send_c("hi")` work; `send_a("hi")` raises `TypeError` for the missing argument. `send_a`'s `to` may be `None`, but it must still be passed.
3. mypy reports `Item "None" of "str | None" has no attribute "upper"` (`[union-attr]`). Check `if to is None:` (and return or assign a default) before using the string.
4. `None` is not a `str`, so the default does not fit the hint; mypy reports an incompatible default. Write `str | None = None`.
