## Hint 1

List what could go wrong before you write a line: a root of `/` or `~` from an empty config; a symlink inside the folder that points somewhere precious; a file exactly at the boundary; a dry run that deletes anyway. Each of these maps to one check. Where must the root check happen so it runs even when the folder is huge?

## Hint 2

```text
refuse_dangerous_root(root):
    r = Path(root).resolve()
    if not r.is_dir() or r == Path(r.anchor) or r == Path.home().resolve(): raise ValueError(...)
    return r
delete_older_than(root, days, now, dry_run=True):
    base = refuse_dangerous_root(root); if days < 0: raise ValueError
    cutoff = (now - timedelta(days=days)).timestamp()
    old = []
    for folder, dirs, files in os.walk(base):              # does not follow symlinked folders
        for name in files:
            p = Path(folder) / name
            if p.is_symlink() or not p.is_file() or not is_inside(p, base): continue
            if p.stat().st_mtime < cutoff: old.append(p)
    old.sort(); if not dry_run: unlink each; return old
```
