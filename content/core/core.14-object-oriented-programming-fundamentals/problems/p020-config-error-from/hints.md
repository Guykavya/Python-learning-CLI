## Hint 1

Where can you write `raise ... from e`? You need the original error object `e`. Which block gives
you a name for it?

## Hint 2

Keep the range check **outside** the `except` block. If you raise inside `except ValueError`, the new
error gets the `ValueError` as its context even without `from`. The out-of-range error has no
low-level cause, so it should be raised after the `try` statement has finished.

## Hint 3

```
class ConfigError(Exception): pass

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
