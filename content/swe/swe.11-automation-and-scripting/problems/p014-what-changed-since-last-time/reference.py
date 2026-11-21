from pathlib import Path


def snapshot(root):
    """{relative/posix/path: (size, mtime_ns)} for every file under root."""
    root = Path(root)
    result = {}
    for p in root.rglob("*"):
        if p.is_file():
            st = p.stat()
            result[p.relative_to(root).as_posix()] = (st.st_size, st.st_mtime_ns)
    return result


def changes(old, new):
    """{'added': [...], 'removed': [...], 'modified': [...]}, each sorted."""
    return {"added": sorted(new.keys() - old.keys()),
            "removed": sorted(old.keys() - new.keys()),
            "modified": sorted(k for k in old.keys() & new.keys() if old[k] != new[k])}
