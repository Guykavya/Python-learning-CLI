- `isinstance(value, list[int])`. Python refuses: "isinstance() argument 2 cannot be a
  parameterized generic". Check the origin, `list`, instead.
- Reading `func.__annotations__` directly. A hint of `None` stays `None` there, and
  `isinstance(x, None)` fails. `get_type_hints` turns it into `type(None)`.
- Calling `apply_defaults()` before checking. Then a default such as `None` for a `str`
  parameter is wrongly reported as a bad argument.
- Checking only positional arguments with `zip(params, args)`. Keyword arguments slip through.
- Calling the function before checking the arguments. The function may already have done
  something with the bad value.
- Accepting only `typing.Union` as the union origin. On some Python versions `int | None`
  reports `type(int | str)` instead.
