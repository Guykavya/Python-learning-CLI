## Hint 1

Dictionary keys behave like sets: `new.keys() - old.keys()` is "only in new". Which set operation gives the keys present in both? For the snapshot: which `Path` method walks the whole tree, and how do you turn `root/sub/c.txt` into the string `"sub/c.txt"` on every system?

## Hint 2

```text
snapshot: {p.relative_to(root).as_posix(): (st.st_size, st.st_mtime_ns) for p in Path(root).rglob("*") if p.is_file()}
changes:
    added    = sorted(new.keys() - old.keys())
    removed  = sorted(old.keys() - new.keys())
    modified = sorted(k for k in old.keys() & new.keys() if old[k] != new[k])
```
