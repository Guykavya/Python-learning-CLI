## Hint 1

`iter(f, "")` can call a function again and again until it returns a marker value. What function takes no
arguments and returns the next chunk? (`functools.partial` or a `lambda` can make one.) What does `read` return
at the end of a binary file?

## Hint 2

```
h = hashlib.sha256()
with open(path, "rb") as f:
    for chunk in iter(lambda: f.read(chunk_size), b""):
        h.update(chunk)
return h.hexdigest()
```
