## Hint 1

`os.walk` gives each folder once, with its own files. How do you turn the absolute `dirpath` into
`"src/util"`? (`Path(dirpath).relative_to(root).as_posix()`.) And when you have the size of the files
in `src/util`, which other folders must also grow by that amount?

## Hint 2

Pruning: inside the loop, `dirnames[:] = [d for d in dirnames if d not in skip]`. It must be a slice
assignment: `dirnames = [...]` only rebinds your local name and `os.walk` still enters the folders.
For the parents, `PurePosixPath("src/util").parents` gives `src` and `.`.

## Hint 3

```
totals = {}
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [names not in skip]
    rel = relative posix path of dirpath   ('.' for root)
    own = sum of getsize for each file
    totals[rel] = totals.get(rel, 0) + own
    if rel != '.': for p in PurePosixPath(rel).parents: totals[p.as_posix()] += own
```

`os.walk` is top-down, so a parent is always in `totals` before its children. For `largest_files`
collect `(rel_file, size)` pairs and sort with `key=lambda t: (-t[1], t[0])`.
