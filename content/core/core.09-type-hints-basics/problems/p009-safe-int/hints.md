## Hint 1

`int("abc")` raises an exception. Which one? (You met it in core.07.) Where does the `try` go, and what do you return in the `except`?

## Hint 2

`safe_int_or` can call `safe_int`. But the result may be `None`: you must check with `is None`, not with `if not result` (because `0` is a valid result). For `parse_all`, a comprehension with a condition can drop the `None` values.

## Hint 3

```
def safe_int(text):
    try: return int(text.strip())
    except ValueError: return None

def safe_int_or(text, default):
    n = safe_int(text)
    if n is None: return default
    return n

def parse_all(texts):
    return [n for n in map(safe_int, texts) if n is not None]
```
