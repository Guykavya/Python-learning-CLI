# What changed since last time?

Chapter section 6.5 (watching a folder by polling). To react to new or edited files you do not need a library: take a **snapshot** of the folder, take another one later, and compare. This is also how many backup and sync tools decide what to copy.

## What to write

```python
def snapshot(root) -> dict[str, tuple[int, int]]: ...
def changes(old, new) -> dict[str, list[str]]: ...
```

- `snapshot(root)` maps the path of every **file** under `root` (recursively, folders themselves not listed) to `(size, mtime_ns)`, using `p.stat().st_size` and `p.stat().st_mtime_ns` (nanoseconds: whole seconds are too coarse for files changed twice in one second). The key is the path **relative to root with forward slashes** (`"sub/b.txt"`, also on Windows: `.as_posix()`).
- `changes(old, new)` returns `{"added": [...], "removed": [...], "modified": [...]}`: keys only in `new`, keys only in `old`, and keys in both whose `(size, mtime_ns)` differ. Each list is sorted.
- Both are pure "look" functions: `changes` compares two dictionaries and never touches the disk, so it can compare a snapshot saved yesterday (as JSON) with one taken now.

## Example

```python
before = snapshot(root)                  # {'a.txt': (1, ...), 'b.txt': (2, ...)}
# a.txt rewritten with 6 bytes, b.txt deleted, sub/c.txt created
changes(before, snapshot(root))
# {'added': ['sub/c.txt'], 'removed': ['b.txt'], 'modified': ['a.txt']}
```
