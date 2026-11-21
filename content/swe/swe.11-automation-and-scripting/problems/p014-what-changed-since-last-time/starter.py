from pathlib import Path


def snapshot(root):
    """{relative/posix/path: (size, mtime_ns)} for every file under root."""
    # TODO
    return {}


def changes(old, new):
    """{'added': [...], 'removed': [...], 'modified': [...]}, each sorted."""
    # TODO
    return {"added": [], "removed": [], "modified": []}
