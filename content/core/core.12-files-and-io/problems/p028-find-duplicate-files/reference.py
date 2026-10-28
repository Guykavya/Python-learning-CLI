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
