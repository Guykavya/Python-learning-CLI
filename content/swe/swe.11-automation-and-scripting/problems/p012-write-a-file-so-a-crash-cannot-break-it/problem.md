# Write a file so a crash cannot break it

Chapter section 6.3 (writing a file so a crash cannot leave half a file). If a script dies while writing `state.json` (power cut, Ctrl+C, disk full), a plain `write_text` leaves a **truncated** file, and the next run may read it as valid. The safe pattern: write a temporary file **in the same folder**, push it to the disk, then atomically **replace** the target. A reader sees the old file or the new one, never half.

## What to write

```python
def atomic_write_text(path, text) -> None: ...
```

- Create the temporary file in `path`'s folder with `tempfile.mkstemp(dir=..., prefix=..., suffix=".tmp")` (same folder means same file system, which `os.replace` needs to be atomic).
- Write `text` encoded as UTF-8, then `flush()` and **`os.fsync(f.fileno())`**.
- Replace the target with **`os.replace(tmp, path)`**.
- If anything fails before the replace finishes (the tests simulate a crash by making `os.fsync` or `os.replace` raise), delete the temporary file and **re-raise**: the old content must still be there, and no `.tmp` file may be left behind.
- It does not create missing folders.

Use `import os` and call `os.fsync` and `os.replace` through the module (the tests watch those two calls).

## Example

```python
atomic_write_text(target, '{"last_run": 1}')
atomic_write_text(target, '{"last_run": 2}')
target.read_text(encoding="utf-8")            # '{"last_run": 2}'
sorted(p.name for p in target.parent.iterdir())   # ['state.json']   (no leftover temp files)
```
