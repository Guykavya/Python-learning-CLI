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
            continue                      # a unique size cannot have a twin: do not read it
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
