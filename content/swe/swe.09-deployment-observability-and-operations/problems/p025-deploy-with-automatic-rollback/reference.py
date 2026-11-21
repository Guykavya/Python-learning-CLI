import os
import re
import shutil
from pathlib import Path, PurePosixPath

VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def current_version(root):
    pointer = Path(root) / "current"
    return pointer.read_text(encoding="utf-8").strip() if pointer.exists() else None


def _write_pointer(root, version):
    pointer = Path(root) / "current"
    tmp = pointer.with_name("current.tmp")
    tmp.write_text(version + "\n", encoding="utf-8")
    os.replace(tmp, pointer)                                     # atomic on every OS: never a half-written pointer


def _validate(version, files):
    if not isinstance(version, str) or not VERSION.match(version):
        raise ValueError(f"invalid version {version!r}")
    for rel in files:
        path = PurePosixPath(rel)
        if not rel or path.is_absolute() or ".." in path.parts or rel.startswith(("/", "\\")) or "\\" in rel:
            raise ValueError(f"invalid file path {rel!r}")


def _prune(root, keep):
    releases = Path(root) / "releases"
    history = (Path(root) / "history.txt").read_text(encoding="utf-8").split()
    existing = [v for v in history if (releases / v).is_dir()]
    live = current_version(root)
    candidates = [v for v in existing if v != live]
    for v in candidates[: max(0, len(existing) - keep)]:
        shutil.rmtree(releases / v)


def deploy(root, version, files, health_check, keep=5):
    root = Path(root)
    _validate(version, files)
    releases = root / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    final = releases / version
    if final.exists():
        raise ValueError(f"release {version} already exists: releases are immutable")
    tmp = releases / f".{version}.tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    try:
        for rel, text in files.items():
            target = tmp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        tmp.mkdir(exist_ok=True)                                 # a release with no files is still a folder
        os.replace(tmp, final)                                   # the release appears complete, or not at all
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    previous = current_version(root)
    _write_pointer(root, version)
    with (root / "history.txt").open("a", encoding="utf-8") as history:
        history.write(version + "\n")
    error = None
    try:
        healthy = bool(health_check(final))
        if not healthy:
            error = "health check failed"
    except Exception as exc:
        healthy, error = False, f"{type(exc).__name__}: {exc}"
    if healthy:
        result = {"version": version, "status": "live", "live": version, "error": None}
    elif previous is not None:
        _write_pointer(root, previous)
        result = {"version": version, "status": "rolled_back", "live": previous, "error": error}
    else:
        (root / "current").unlink()
        result = {"version": version, "status": "failed", "live": None, "error": error}
    _prune(root, keep)
    return result
