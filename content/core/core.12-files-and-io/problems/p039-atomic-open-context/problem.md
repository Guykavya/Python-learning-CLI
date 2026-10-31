# atomic_open: write all or nothing

Build a tool that makes any `with open(...)` block safe. Write `atomic_open(path, mode="w", **kwargs)` in
`solution.py` with `@contextlib.contextmanager`:

- It yields a file object that writes to a **temporary file in the same folder** as `path`.
  `mode` is `"w"` (text) or `"wb"` (bytes). `kwargs` (for example `encoding="utf-8"`) go to the file.
- While the block runs, `path` itself is **not touched**: an old file keeps its old content, and a new file does
  not exist yet.
- If the block ends normally, the temp file is closed and moved over `path` with `os.replace`.
- If the block raises an error, the temp file is **deleted**, `path` stays exactly as it was, and the error goes up.
- When the call is over, the folder holds no leftover temp files.

Use `tempfile.mkstemp(dir=...)` and `os.fdopen`, or just `open` on a temp name next to `path`.

**Example**

```python
with atomic_open("config.txt") as f:
    f.write("new content\n")
    raise RuntimeError("crash")
# config.txt still has its old content, and no temp file is left
```
