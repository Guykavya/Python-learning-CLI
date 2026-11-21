# Delete old files, safely

Chapter sections 6.4 (deleting safely, `is_inside`) and "Try it: what could go wrong?". Deleting is the one operation you cannot undo. A cleanup job that deletes files older than N days is useful, and also the classic way to wipe a home folder because a config value was empty. Build it so the dangerous mistakes are impossible.

## What to write

```python
def is_inside(child, parent) -> bool: ...                 # given in the starter (chapter 6.4)
def refuse_dangerous_root(root) -> Path: ...
def delete_older_than(root, days, now, dry_run=True) -> list[Path]: ...
```

`refuse_dangerous_root(root)` returns `Path(root).resolve()` if it is safe to clean, and raises `ValueError` if it is:
- not an existing folder;
- the top of a file system (`/`, or `C:\` on Windows: the resolved path equals its own `anchor`);
- your home folder (`Path.home()`, resolved).

`delete_older_than(root, days, now, dry_run=True)`:
- calls `refuse_dangerous_root(root)` **first**, before looking at any file; `days` below 0 is a `ValueError` too;
- walks the tree **without following symbolic links** (`os.walk` does not follow them by default) and considers only **regular files that are not symlinks** and that are inside the root (`is_inside`);
- a file is old when its modification time is **strictly** before `now - timedelta(days=days)`; `now` is a `datetime` passed in by the caller (never read the clock in this function: that is what makes "older than 30 days" testable to the second);
- is a **dry run by default**: it only returns what it would delete. With `dry_run=False` it deletes those files (never folders);
- returns the old files as a sorted list of `Path`s.

## Example

```python
now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
# logs/old.log is 40 days old, logs/new.log 1 day old
delete_older_than(root, 30, now)                    # [root/'logs/old.log']   (nothing deleted: dry run)
delete_older_than(root, 30, now, dry_run=False)     # [root/'logs/old.log']   (now really deleted)
delete_older_than(Path.home(), 30, now)             # ValueError: refusing to clean your home folder
```

The tests set file times with `os.utime`, pass a fixed `now`, and replace `Path.home()` with a temporary folder, so nothing outside the test folder is ever touched.
