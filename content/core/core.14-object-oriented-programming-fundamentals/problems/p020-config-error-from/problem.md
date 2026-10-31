# Turn low-level errors into a ConfigError with `raise from`

A config loader that crashes with `ValueError: invalid literal for int() with base 10: 'eighty'`
makes the user guess what went wrong. Better: raise **your own** `ConfigError` with a clear message,
and attach the original error as its **cause** with `raise ... from e`. The traceback then shows both:
the low-level reason and the high-level meaning.

Write in `solution.py`:

- `ConfigError`, a subclass of `Exception`.
- `parse_port(text)` returns the port number as an `int`.
  - Spaces around the text are allowed: `" 8080 "` gives `8080`.
  - If `int()` fails, raise `ConfigError(f"port must be a number, got {text!r}")` **from** the
    `ValueError`.
  - If the number is not between 1 and 65535, raise `ConfigError(f"port out of range: {number}")`.
    There is no lower-level error here, so do not chain it.
- `load_port(settings)` takes a dict and returns `parse_port(settings["port"])`.
  - If the key `"port"` is missing, raise `ConfigError("missing setting: port")` **from** the `KeyError`.
  - Errors from `parse_port` pass through unchanged.

**Example**

```python
print(parse_port(" 8080 "))         # 8080
try:
    parse_port("eighty")
except ConfigError as e:
    print(e)                         # port must be a number, got 'eighty'
    print(type(e.__cause__).__name__)  # ValueError
parse_port("70000")                  # ConfigError: port out of range: 70000
load_port({"host": "x"})             # ConfigError: missing setting: port
```
