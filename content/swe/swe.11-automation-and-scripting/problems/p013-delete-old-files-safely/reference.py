import os
from datetime import timedelta
from pathlib import Path


def is_inside(child, parent):
    """True if child is parent or lies under it, after resolving '..' and symlinks (chapter 6.4)."""
    child, parent = Path(child).resolve(), Path(parent).resolve()
    return parent == child or parent in child.parents


def refuse_dangerous_root(root):
    """Return Path(root).resolve(), or raise ValueError for a missing folder, a file-system top, or the home folder."""
    resolved = Path(root).resolve()
    if not resolved.is_dir():
        raise ValueError(f"{root} is not a folder")
    if resolved == Path(resolved.anchor):
        raise ValueError(f"refusing to clean the top of a file system: {resolved}")
    if resolved == Path.home().resolve():
        raise ValueError("refusing to clean your home folder")
    return resolved


def delete_older_than(root, days, now, dry_run=True):
    """Files under root (no symlinks) modified strictly before now - days. Deleted only if dry_run is False."""
    base = refuse_dangerous_root(root)
    if days < 0:
        raise ValueError("days must not be negative")
    cutoff = (now - timedelta(days=days)).timestamp()
    old = []
    for folder, _dirs, files in os.walk(base):          # os.walk does not follow symlinked folders
        for name in files:
            p = Path(folder) / name
            if p.is_symlink() or not p.is_file() or not is_inside(p, base):
                continue
            if p.stat().st_mtime < cutoff:
                old.append(p)
    old.sort()
    if not dry_run:
        for p in old:
            p.unlink()
    return old
