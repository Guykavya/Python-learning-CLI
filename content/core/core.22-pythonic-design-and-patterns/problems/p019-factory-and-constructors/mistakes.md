- Registering an *instance* (`EXPORTERS["json"] = JsonExporter()`) and returning it every time:
  all callers share one object. Store the class and call it.
- A decorator that forgets `return cls`: the name `JsonExporter` becomes `None`.
- Writing `Money(...)` inside `from_string`: `Euro.from_string` then returns a plain `Money`.
- Writing `from_string` as a normal method or `@staticmethod`; it has no way to know the class. Use `@classmethod`.
- `"7.5"` parsed as 705 cents: the fraction must be padded to two digits.
- Error messages that do not list the known formats, or list them in dict order instead of sorted.
- Raising `KeyError` for an unknown format; the statement asks for `ValueError`.
