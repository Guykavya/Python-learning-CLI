## Approach

Translate errors at the border of your code (chapter section 18). Inside the `except` block you have
the original error as `e`; `raise ConfigError(...) from e` sets the new error's `__cause__` to `e`, and
the traceback says "The above exception was the direct cause of the following exception".

Two details:

- The range check sits **after** the `try` statement. If it were inside the `except` block, the new error
  would carry the `ValueError` as its `__context__` ("During handling of the above exception, another
  exception occurred"), which is misleading: a number like 70000 parsed just fine.
- In `load_port`, only the dict lookup goes in the `try`. `parse_port` is called afterwards, so its
  `ConfigError`s pass through as they are.

## Code

```python
class ConfigError(Exception):
    pass


def parse_port(text):
    try:
        number = int(text.strip())
    except ValueError as e:
        raise ConfigError(f"port must be a number, got {text!r}") from e
    if not 1 <= number <= 65535:
        raise ConfigError(f"port out of range: {number}")
    return number


def load_port(settings):
    try:
        text = settings["port"]
    except KeyError as e:
        raise ConfigError("missing setting: port") from e
    return parse_port(text)
```

## Complexity

O(k) for a text of length k (for `strip` and `int`).

## Another way

`raise ConfigError(...) from None` hides the original error completely (`__cause__` is `None` and
`__suppress_context__` is `True`). Use it when the low-level detail is only noise for the user. Since
Python 3.11 you can also add extra lines to any error with `e.add_note("while reading config.toml")`
and re-raise it unchanged.
