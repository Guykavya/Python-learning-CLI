## Approach

Wrap the open-and-read in `try` and catch `FileNotFoundError` only. `PermissionError`, `IsADirectoryError` and others are different `OSError` subclasses. Hiding them would hide real problems, such as a wrong path or no rights. Returning inside `with` is fine: the file is closed on the way out.

## Code

```python
def read_or_default(path, default=""):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return default
```

## Complexity

O(n) for the file size.

## Another way

Check first with `os.path.exists(path)` and then open. It looks safe, but the file can vanish between the check and the open (a race). Asking forgiveness with `try/except` is the usual Python style.
