## Approach

A two-stage filter. Stage one groups by `stat().st_size`, which costs nothing (no file is read).
Any size that appears once is dropped. Stage two hashes only the survivors and groups them by digest.
Different content with the same size (`hello` / `world`) lands in different hash groups. Sorting each
group and then the list makes the output the same on every computer, whatever order the file system
returns the names in.

## Code

```python
import hashlib
from collections import defaultdict
from pathlib import Path


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(root):
    root = Path(root)
    by_size = defaultdict(list)
    for path in root.rglob("*"):
        if path.is_file():
            size = path.stat().st_size
            if size > 0:
                by_size[size].append(path)

    groups = []
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        by_hash = defaultdict(list)
        for path in same_size:
            by_hash[file_hash(path)].append(path.relative_to(root).as_posix())
        for names in by_hash.values():
            if len(names) >= 2:
                groups.append(sorted(names))
    return sorted(groups)


def wasted_bytes(root, groups):
    root = Path(root)
    total = 0
    for group in groups:
        size = (root / group[0]).stat().st_size
        total += size * (len(group) - 1)
    return total
```

## Complexity

Listing: O(F) for F files. Hashing reads only the bytes of files whose size is shared: in the worst
case all bytes (O(total size)), often far fewer. Sorting the groups: O(F log F).

## Another way

Real tools add a third stage between size and full hash: hash only the **first 4 KiB** of each
candidate. Files that differ early are separated after reading very little, and the full hash is
needed only for the few that still match. For absolute certainty you can compare the final
candidates byte by byte with `filecmp.cmp(a, b, shallow=False)`: SHA-256 collisions are not a
practical worry, but the byte comparison costs little once you are down to a few files.
