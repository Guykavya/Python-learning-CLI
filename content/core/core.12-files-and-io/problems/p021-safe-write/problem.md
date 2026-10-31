# Replace a file safely

If a program crashes while it writes a file with mode `"w"`, the old content is already gone and the new
content is only half there. A **safe write** never leaves a broken file.

Write `safe_write(path, text)` in `solution.py`:

1. Write `text` (UTF-8) to a **temporary file in the same folder** as `path`.
2. Only when that worked, replace `path` with it using `os.replace`.
3. If anything goes wrong while writing (for example `text` is not a string), the old file must stay
   exactly as it was, the **error must still be raised**, and no temporary file may be left behind.

`path` may be a `str` or a `Path`. It may not exist yet.

**Example**

```python
safe_write("data.txt", "new text\n")      # replaces data.txt in one step
safe_write("data.txt", b"bytes!")         # raises TypeError; data.txt still holds "new text\n"
```
