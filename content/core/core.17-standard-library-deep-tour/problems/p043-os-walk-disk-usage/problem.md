# Disk usage per folder with `os.walk`

`os.walk(root)` visits every folder under `root` and gives you, for each one, a tuple
`(dirpath, dirnames, filenames)`. Two details make it more powerful than `Path.rglob`:

- With the default `topdown=True`, you may **change `dirnames` in place** (`dirnames[:] = ...`) to stop
  the walk from going into some folders: this is called *pruning* (think `.git` or `__pycache__`).
- You see each folder exactly once with its own files, which is just what you need to add up sizes.

Write three functions in `solution.py`. All paths in results are **relative to `root`** and written
with forward slashes (`Path.as_posix()`), so the results are the same on Windows and Linux.

1. `disk_usage(root, skip=()) -> dict[str, int]`
   Maps every folder to the **total** size in bytes of all files inside it, *including its
   sub-folders*. The root itself is `"."`. Empty folders appear with `0`. Folders whose **name** is in
   `skip` are not entered and do not appear at all (their files are not counted anywhere).
2. `largest_files(root, n, skip=()) -> list[tuple[str, int]]`
   The `n` biggest files as `(relative_path, size)`, biggest first; equal sizes in alphabetical order
   of the path. Same `skip` rule.
3. `human_size(nbytes) -> str`
   Below 1024: `"512 B"`. Otherwise divide by 1024 until the value is below 1024 (or you reach `TiB`)
   and show one decimal with the unit: `"1.5 KiB"`, `"2.0 MiB"`, `"1.0 GiB"`, `"3.0 TiB"`.

**Example**

```text
project/
    a.txt          (100 bytes)
    src/
        main.py    (300 bytes)
        util/
            u.py   (50 bytes)
    .git/
        objects    (5000 bytes)
    empty/
```

```python
disk_usage("project", skip={".git"})
# {'.': 450, 'src': 350, 'src/util': 50, 'empty': 0}

largest_files("project", 2, skip={".git"})
# [('src/main.py', 300), ('a.txt', 100)]

human_size(1536)        # '1.5 KiB'
```

The order of the keys in the dict does not matter.
