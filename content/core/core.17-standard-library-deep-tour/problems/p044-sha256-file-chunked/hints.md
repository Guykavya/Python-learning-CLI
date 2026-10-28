## Hint 1

`hashlib.sha256()` gives an empty hash object. What method adds bytes to it, and can you call it many
times? When does `f.read(chunk_size)` tell you the file is finished?

## Hint 2

The read loop: `chunk = f.read(chunk_size)`; if `chunk` is `b""` stop, otherwise `h.update(chunk)`.
For text, hash `text.encode("utf-8")`. For `matches`, clean the expected value with
`.strip().lower()` before comparing.

## Hint 3

```
sha256_stream(f, size):
    h = hashlib.sha256()
    loop:
        chunk = f.read(size)
        if not chunk: break
        h.update(chunk)
    return h.hexdigest()

sha256_file(path, size):
    with open(path, "rb") as f: return sha256_stream(f, size)
```
