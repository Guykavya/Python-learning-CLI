## Approach

Two passes. Pass 1 groups by size using only `stat`, which does not read the file. A file with a size that nobody
else has can never be a duplicate, so it is never opened. Pass 2 hashes only the files in groups of two or more and
groups them by the digest. Sort every group and the list of groups so that the answer does not depend on the
order the disk returns files.

## Code

```python
import hashlib
from pathlib import Path


def _digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(root):
    root = Path(root)
    by_size = {}
    for p in root.rglob("*"):
        if p.is_file():
            by_size.setdefault(p.stat().st_size, []).append(p)

    groups = []
    for paths in by_size.values():
        if len(paths) < 2:
            continue
        by_hash = {}
        for p in paths:
            by_hash.setdefault(_digest(p), []).append(p.relative_to(root).as_posix())
        for names in by_hash.values():
            if len(names) >= 2:
                groups.append(sorted(names))
    return sorted(groups)
```

## Complexity

Time O(N) for the stat pass plus O(bytes of files that share a size). Memory O(number of files).

## Another way

Hash everything directly: simpler but reads every file. Or compare the first 1 KB first, as a second cheap filter.
