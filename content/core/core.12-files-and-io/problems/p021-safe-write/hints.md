## Hint 1

What happens to the old file if you open it with `"w"` and the writing fails half way? Which operation replaces a file in one step, so that readers see either the old or the new file?

## Hint 2

```
fd, tmp = tempfile.mkstemp(dir=folder)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)
except BaseException:
    remove tmp if it exists
    raise
```
