- `except:` or `except Exception:` around the file read. A `PermissionError` or a bug in your code
  becomes "file missing".
- `try: return obj.name.upper() except AttributeError:` also catches an `AttributeError` raised
  inside the property or by `.upper()` on a non-string. Read the attribute alone in the `try`.
- Keeping `if "port" in config` and adding `.get` inside it: still two lookups.
- `config.get("port") or 8080`: a port of `0` becomes 8080 (see p002).
- Catching `Exception` in `parse_int`; `int(None)` raises `TypeError`, and hiding it may hide a bug.
  Catch `ValueError` (add `TypeError` only if `None` is allowed input).
- Calling `fs.exists(path)` "just to be safe" before `open`. That is the race EAFP avoids.
