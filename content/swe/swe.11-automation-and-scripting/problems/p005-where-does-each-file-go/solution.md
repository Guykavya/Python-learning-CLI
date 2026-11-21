## Approach

```python
def category_for(path):
    return CATEGORIES.get(Path(path).suffix.lower(), "other")


def unique_destination(dst):
    """Never overwrite: if 'a.txt' exists, use 'a (1).txt', 'a (2).txt'..."""
    dst = Path(dst)
    if not dst.exists():
        return dst
    n = 1
    while True:
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not candidate.exists():
            return candidate
        n += 1
```

`category_for` is pure (it only looks at the name), so it is trivial to test. `unique_destination` asks the file system, but only reads: the decision "where does it go" stays separate from the action "move it", which is what makes a dry run possible later (p006).

## Complexity

`category_for` is O(1). `unique_destination` makes k + 1 `exists()` checks when k names are taken.

## Another way

Add a timestamp instead of a counter (`a 2026-11-21 0930.txt`). It is unique without a loop, but uglier, and two moves in the same minute still collide, so you need the loop anyway. The counter is what file managers do.

Note: there is a tiny race between "it does not exist" and the later move (another program could create the file in between). For a personal tool that is acceptable; when it is not, open the destination with `os.open(..., O_CREAT | O_EXCL)` as the lock of section 12.4 does.
