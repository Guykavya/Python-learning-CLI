## Approach

A hash object keeps a running state. Calling `update` many times with pieces is the same as calling it once with
all the bytes put together. So read piece by piece. `iter(callable, sentinel)` calls the callable until it returns the
sentinel. In binary mode `read` returns `b""` at the end of the file (not `""`).

## Code

```python
import hashlib


def file_sha256(path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
```

## Complexity

Time O(file size). Memory O(chunk_size).

## Another way

A `while True:` loop with `chunk = f.read(chunk_size)` and `if not chunk: break`. In Python 3.11 and later you can
also use `hashlib.file_digest(f, "sha256")`.
