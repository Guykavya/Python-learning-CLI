## Approach

Walk once with `os.walk`. In each folder:

1. Prune: replace the **contents** of `dirnames` so `os.walk` will not descend into skipped folders.
2. Compute the folder's relative posix name (`"."` for the root).
3. Add the size of its own files to itself **and** to every ancestor (`PurePosixPath(rel).parents`).

Because the walk is top-down, parents are recorded before their children. A small generator
`_walk_files` is shared by `disk_usage` and `largest_files`, so the pruning rule is written once.

## Code

```python
import os
from pathlib import Path, PurePosixPath


def _walk_files(root, skip):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in skip)   # prune in place
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        files = []
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = name if rel_dir == "." else f"{rel_dir}/{name}"
            files.append((rel, os.path.getsize(full)))
        yield rel_dir, files


def disk_usage(root, skip=()):
    totals = {}
    for rel_dir, files in _walk_files(root, skip):
        totals.setdefault(rel_dir, 0)
        own = sum(size for _, size in files)
        totals[rel_dir] += own
        if rel_dir != ".":
            for parent in PurePosixPath(rel_dir).parents:
                totals[parent.as_posix()] += own
    return totals


def largest_files(root, n, skip=()):
    all_files = []
    for _, files in _walk_files(root, skip):
        all_files.extend(files)
    all_files.sort(key=lambda item: (-item[1], item[0]))
    return all_files[:n]


def human_size(nbytes):
    if nbytes < 1024:
        return f"{nbytes} B"
    value = float(nbytes)
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        value /= 1024
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}"
```

## Complexity

For F files in D folders of depth at most h: O(F + D·h) for `disk_usage` (each folder's total is
added to its ancestors) and O(F log F) for `largest_files` (the sort). `heapq.nlargest(n, ...)` would
make it O(F log n).

## Another way

Walk **bottom-up** with `os.walk(root, topdown=False)`: then every child is finished before its
parent, and a parent's total is its own files plus its children's totals. But pruning only works
top-down (bottom-up has already visited the children), so you would have to filter skipped paths
afterwards. `Path.rglob("*")` also works for listing files but cannot prune at all: it walks into
`.git` and throws the results away.
