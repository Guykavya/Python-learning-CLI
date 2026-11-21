## Approach

```python
def refuse_dangerous_root(root):
    resolved = Path(root).resolve()
    if not resolved.is_dir():
        raise ValueError(f"{root} is not a folder")
    if resolved == Path(resolved.anchor):
        raise ValueError(f"refusing to clean the top of a file system: {resolved}")
    if resolved == Path.home().resolve():
        raise ValueError("refusing to clean your home folder")
    return resolved


def delete_older_than(root, days, now, dry_run=True):
    base = refuse_dangerous_root(root)
    if days < 0:
        raise ValueError("days must not be negative")
    cutoff = (now - timedelta(days=days)).timestamp()
    old = []
    for folder, _dirs, files in os.walk(base):
        for name in files:
            p = Path(folder) / name
            if p.is_symlink() or not p.is_file() or not is_inside(p, base):
                continue
            if p.stat().st_mtime < cutoff:
                old.append(p)
    old.sort()
    if not dry_run:
        for p in old:
            p.unlink()
    return old
```

Every line answers one of the chapter's "what could go wrong?": the root guard catches the empty or wrong config **before** any file is listed; skipping symlinks means a link to `~/Documents` is never followed or deleted through; `is_inside` on resolved paths is a second net; the dry run is the default, so forgetting a flag is harmless; and `now` is a parameter, so the boundary (exactly 30 days is kept) is tested to the second instead of "roughly".

## Complexity

O(n log n) for n files under the root (one `stat` each, then a sort).

## Another way

Move old files to a dated trash folder (`trash/2026-11-21/...`) instead of deleting them, and empty the trash with a separate command a week later (section 6.4). The function stays the same; only the last loop changes from `unlink` to a move. That turns an unrecoverable mistake into a recoverable one.
