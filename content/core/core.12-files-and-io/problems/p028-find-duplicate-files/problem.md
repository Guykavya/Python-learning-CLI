# Find duplicate files

Two files are duplicates when they have the **same bytes**, whatever their names or folders.
Hashing every file is slow. Files with different sizes cannot be equal, so first group by size, and hash
only the files that share a size.

Write `find_duplicates(root)` in `solution.py`:

- Look at every **file** below `root` (all levels). Folders are not files.
- Return a list of groups. A group is a **sorted list of relative paths** (strings, with `/` as separator, e.g.
  `"photos/a.jpg"`) of files that are equal. Only groups with **two or more** files are returned.
- The groups are sorted too (a list of lists compares item by item, so `sorted(groups)` works).
- Files with the same size but different content must **not** be grouped. Two empty files are duplicates.

Use `Path.rglob`, `stat().st_size`, `Path.relative_to(root).as_posix()` and `hashlib`.

**Example**

```text
root/a.txt        "hello"
root/sub/b.txt    "hello"
root/c.txt        "world"
root/sub/d.txt    "hellp"
```

`find_duplicates(root)` returns `[["a.txt", "sub/b.txt"]]`.
