import os
from pathlib import Path, PurePosixPath


def _walk_files(root, skip):
    """Yield (relative_dir, [(relative_file, size), ...]) for every folder not skipped."""
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
            for parent in PurePosixPath(rel_dir).parents:   # 'a/b' -> 'a', '.'
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
