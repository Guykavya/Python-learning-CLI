## Hint 1

Where must the temp file live so that `os.replace` is a cheap rename? What must happen to it in each of the two cases,
the block finishes or the block raises? Which keyword runs code in both cases, and which one only on error?

## Hint 2

```
path = Path(path)
fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
try:
    with os.fdopen(fd, mode, **kwargs) as f:
        yield f
    os.replace(tmp, path)
except BaseException:
    Path(tmp).unlink(missing_ok=True)
    raise
```
