## Hint 1

Which tool of `tempfile` creates a folder and deletes it for you when a `with` block ends?

## Hint 2

```
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "work.txt"
    path.write_text(...)   # or open()
    lines = ... read back and sort
    return sorted(lines), str(path)
```
The cleanup runs when the `with` block ends, even with `return` inside it.
