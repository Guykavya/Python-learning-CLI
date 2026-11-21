import shutil
from pathlib import Path


def current_version(root):
    pointer = Path(root) / "current"
    return pointer.read_text(encoding="utf-8").strip() if pointer.exists() else None


def deploy(root, version, files, health_check):
    root = Path(root)
    releases = root / "releases"
    previous = current_version(root)

    (root / "current").write_text(version, encoding="utf-8")            # switch first...
    target = releases / version
    for rel, text in files.items():                                       # ...then write the release
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    if previous:                                                          # "save disk space"
        shutil.rmtree(releases / previous)

    return bool(health_check(target))                                     # and hope
