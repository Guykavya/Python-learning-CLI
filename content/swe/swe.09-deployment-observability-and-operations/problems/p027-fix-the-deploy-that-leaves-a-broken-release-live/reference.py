import os
import shutil
from pathlib import Path


def current_version(root):
    pointer = Path(root) / "current"
    return pointer.read_text(encoding="utf-8").strip() if pointer.exists() else None


def _write_pointer(root, version):
    pointer = Path(root) / "current"
    tmp = pointer.with_name("current.tmp")
    tmp.write_text(version, encoding="utf-8")
    os.replace(tmp, pointer)                                              # atomic: never a half-written pointer


def deploy(root, version, files, health_check):
    root = Path(root)
    releases = root / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    previous = current_version(root)

    tmp = releases / f".{version}.tmp"                                    # 1. build the release out of sight
    if tmp.exists():
        shutil.rmtree(tmp)
    try:
        for rel, text in files.items():
            path = tmp / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        tmp.mkdir(exist_ok=True)
        target = releases / version
        os.replace(tmp, target)                                           # 2. complete or absent
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise

    _write_pointer(root, version)                                         # 3. switch only now; the old release is kept
    try:
        healthy = bool(health_check(target))
    except Exception:
        healthy = False
    if healthy:
        return True
    if previous is not None:                                              # 4. a failed check restores the old version
        _write_pointer(root, previous)
    else:
        (root / "current").unlink()
    return False
