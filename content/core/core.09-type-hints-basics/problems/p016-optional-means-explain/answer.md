**1. What `Optional[str]` means.** It is the older spelling of `str | None`: the value is a `str`
**or** `None`. It describes a *value*. This course writes `to: str | None`, because it says
exactly what it means.

**2. Is Meera right?** No. `Optional` says nothing about leaving an argument out. What decides that
is a **default value**, the `= ...` in the header. `send_b("hi")` works because `to` defaults to
`"everyone"`, and `send_c("hi")` works because `to` defaults to `None`. `send_a("hi")` fails with a
`TypeError` (missing argument): `to` may be `None`, but the caller must still pass it, for example
`send_a("hi", None)`.

**3. Using `to.upper()`.** Calling it directly makes mypy report `Item "None" of "str | None" has
no attribute "upper"` (`[union-attr]`), because `to` might be `None`. The fix is to narrow first:
`if to is None: to = "everyone"` (or return early). After that check, mypy knows `to` is a `str`.

**4. `to: str = None`.** `None` is not a `str`, so the default contradicts the hint, and mypy
reports an incompatible default. The honest version is `to: str | None = None`.
