import hashlib
from pathlib import Path


def sha256_of(path, chunk=1024 * 1024):
    """Hex SHA-256 of a file, read in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:                     # read in chunks: works for huge files
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def find_duplicates(root, min_size=1):
    """Groups of files with identical content. Cheap check (size) first, expensive hash second."""
    by_size = {}
    for p in Path(root).rglob("*"):
        if p.is_file() and not p.is_symlink() and p.stat().st_size >= min_size:
            by_size.setdefault(p.stat().st_size, []).append(p)
    groups = []
    for paths in by_size.values():
        if len(paths) > 1:
            by_hash = {}
            for p in paths:
                by_hash.setdefault(sha256_of(p), []).append(p)
            groups += [sorted(g) for g in by_hash.values() if len(g) > 1]
    return sorted(groups)
