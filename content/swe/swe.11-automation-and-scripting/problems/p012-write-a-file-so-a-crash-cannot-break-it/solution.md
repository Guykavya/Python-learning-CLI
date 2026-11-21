## Approach

```python
def atomic_write_text(path, text):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())               # make sure the bytes reached the disk
        os.replace(tmp, path)                  # atomic on the same file system
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
```

Each line removes one failure mode. The temp file is in the **same folder**, because `os.replace` is only atomic within one file system (a temp file in `/tmp` might be on another disk, and then the "move" becomes copy-and-delete). `flush` empties Python's buffer, `fsync` asks the operating system to put the bytes on the disk, so a power cut right after the replace cannot leave an empty new file. `except BaseException` also covers Ctrl+C (`KeyboardInterrupt`), and the bare `raise` keeps the original error for the caller.

## Complexity

O(size of text). One extra file creation and rename per write.

## Another way

Libraries such as `atomicwrites` wrap the same steps. For very strict needs (a database), you would also `fsync` the **folder** after the rename so the new directory entry is durable; SQLite does this kind of thing for you, which is one more reason to keep important state in SQLite (swe.03).
