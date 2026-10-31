## Hint 1

Which exception does `open()` raise for a missing file? Is it the only thing that can go wrong when opening?

## Hint 2

```
try:
    with open(path, encoding="utf-8") as f:
        return f.read()
except FileNotFoundError:
    return default
```
Do not write a bare `except:` or `except OSError`.
