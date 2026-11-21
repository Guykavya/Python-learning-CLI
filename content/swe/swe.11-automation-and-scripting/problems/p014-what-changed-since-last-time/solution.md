## Approach

```python
def snapshot(root):
    root = Path(root)
    result = {}
    for p in root.rglob("*"):
        if p.is_file():
            st = p.stat()
            result[p.relative_to(root).as_posix()] = (st.st_size, st.st_mtime_ns)
    return result


def changes(old, new):
    return {"added": sorted(new.keys() - old.keys()),
            "removed": sorted(old.keys() - new.keys()),
            "modified": sorted(k for k in old.keys() & new.keys() if old[k] != new[k])}
```

Size and modification time together are a cheap fingerprint: a changed file almost always has a new mtime, and a changed size catches the rest. Relative keys with forward slashes make a snapshot portable: saved as JSON on one machine, compared on another.

## Complexity

`snapshot` is O(n) `stat` calls; `changes` is O(n log n) for the sorting.

## Another way

When you must be sure (a tool restored a file with its old mtime, or a file system with coarse timestamps), add a content hash to the fingerprint, but only for files whose size and mtime look unchanged and that matter, as `rsync --checksum` does. It costs a full read of every file, so it is the exception, not the default. For real-time events instead of polling, `watchdog` (`pip install watchdog`) calls you when something changes.
