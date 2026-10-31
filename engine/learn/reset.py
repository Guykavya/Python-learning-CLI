"""Start over: back up and then erase everything that belongs to the learner.

Only the learner's own files are ever touched: progress, solutions and the private
Git history. The course itself (`content/`, `syllabus.yaml`) and the engine are never deleted.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from learn import paths

# Erased by a normal reset: what you did while learning.
PROGRESS = (
    ("data", "your progress tracker (reviews, scores, history of attempts)"),
    ("my-work", "your solutions to every problem"),
    (".progress.git", "the private history of your work"),
)
# Erased only with --all: your settings and files you made or collected yourself.
OWN_FILES = (
    ("config.toml", "your settings (daily minutes, LeetCode and Codeforces names)"),
    ("playground", "your own practice files"),
    ("library", "books and notes you dropped in"),
)
BACKUP_DIR = "backups"


@dataclass
class Target:
    name: str
    what: str
    path: Path
    files: int
    size: int


def _measure(path: Path) -> tuple[int, int]:
    if path.is_symlink() or path.is_file():
        return 1, path.stat().st_size if path.exists() else 0
    files = size = 0
    for f in path.rglob("*"):
        if f.is_file() and not f.is_symlink():
            files += 1
            size += f.stat().st_size
    return files, size


def targets(everything: bool = False) -> list[Target]:
    """What exists right now and would be erased."""
    root = paths.root()
    found = []
    for name, what in PROGRESS + (OWN_FILES if everything else ()):
        p = root / name
        if p.exists() or p.is_symlink():
            files, size = _measure(p)
            found.append(Target(name, what, p, files, size))
    return found


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def make_backup(items: list[Target]) -> Path:
    """Zip the items into backups/. Raises if anything goes wrong, so nothing is erased."""
    root = paths.root()
    folder = root / BACKUP_DIR
    folder.mkdir(exist_ok=True)
    zip_path = folder / f"learn-backup-{datetime.now():%Y%m%d-%H%M%S}.zip"
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for t in items:
                if t.path.is_file():
                    zf.write(t.path, t.path.relative_to(root).as_posix())
                    continue
                for f in sorted(t.path.rglob("*")):
                    if f.is_file() and not f.is_symlink():
                        zf.write(f, f.relative_to(root).as_posix())
        with zipfile.ZipFile(zip_path) as zf:
            bad = zf.testzip()
            if bad:
                raise OSError(f"the backup is damaged at {bad}")
    except Exception:
        zip_path.unlink(missing_ok=True)
        raise
    return zip_path


def _force_remove(func, path, _exc):
    """Windows keeps Git's object files read-only; make them writable and retry."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_tree(path: Path) -> None:
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_force_remove)
    else:
        shutil.rmtree(path, onerror=lambda f, p, e: _force_remove(f, p, e))


def erase(items: list[Target]) -> None:
    root = paths.root().resolve()
    for t in items:
        # Never follow a path out of the learning folder.
        if root not in t.path.resolve().parents and not t.path.is_symlink():
            raise OSError(f"refusing to erase {t.path}: it is outside {root}")
        if t.path.is_symlink() or t.path.is_file():
            if t.path.is_file() and not os.access(t.path, os.W_OK):
                os.chmod(t.path, stat.S_IWRITE)
            t.path.unlink()
        else:
            _remove_tree(t.path)
