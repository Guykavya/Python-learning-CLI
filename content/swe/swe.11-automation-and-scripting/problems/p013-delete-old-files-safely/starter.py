import os
from datetime import timedelta
from pathlib import Path


def is_inside(child, parent):
    """True if child is parent or lies under it, after resolving '..' and symlinks (chapter 6.4)."""
    child, parent = Path(child).resolve(), Path(parent).resolve()
    return parent == child or parent in child.parents


def refuse_dangerous_root(root):
    """Return Path(root).resolve(), or raise ValueError for a missing folder, a file-system top, or the home folder."""
    # TODO
    return Path(root).resolve()


def delete_older_than(root, days, now, dry_run=True):
    """Files under root (no symlinks) modified strictly before now - days. Deleted only if dry_run is False."""
    # TODO
    return []
