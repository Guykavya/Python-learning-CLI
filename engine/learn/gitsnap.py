"""Automatic Git snapshots so your work history is never lost.

Your own files (solutions, tracker, settings) are saved in a private history kept in
`.progress.git/`, separate from the course repository. The course repo can then be
published and updated with `git pull` without your progress ever mixing into it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from learn import paths

GITIGNORE = """\
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
build/
dist/
library/*.pdf
.progress.git/
config.toml
data/
my-work/
backups/
"""

# What belongs to the learner, relative to the project root.
PERSONAL = ("my-work", "data", "playground", "library", "config.toml")
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv"}
SKIP_SUFFIXES = {".pyc", ".pdf"}


def git_dir() -> Path:
    return paths.root() / ".progress.git"


def _git(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    cmd = ["git", f"--git-dir={git_dir()}", f"--work-tree={paths.root()}", *args]
    return subprocess.run(cmd, cwd=paths.root(), input=stdin, capture_output=True, text=True, encoding="utf-8")


def is_repo() -> bool:
    return git_dir().exists()


def _personal_files() -> list[str]:
    root = paths.root()
    found = []
    for name in PERSONAL:
        top = root / name
        candidates = [top] if top.is_file() else top.rglob("*") if top.is_dir() else []
        for f in candidates:
            if not f.is_file() or f.suffix in SKIP_SUFFIXES:
                continue
            if SKIP_DIRS.intersection(f.relative_to(root).parts):
                continue
            found.append(f.relative_to(root).as_posix())
    return found


def init() -> str:
    gi = paths.root() / ".gitignore"
    if not gi.exists():
        gi.write_text(GITIGNORE, encoding="utf-8")
    if is_repo():
        return "Your private progress history already exists."
    try:
        r = subprocess.run(["git", "init", "-q", "--bare", str(git_dir())], capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return "Git is not installed, so your work will not be saved to a history."
    if r.returncode != 0:
        return f"git init failed: {r.stderr.strip()}"
    _git("config", "core.bare", "false")
    return "Created a private history for your work in .progress.git/."


def snapshot(message: str) -> bool:
    """Commit your changed files to the private history. Silent no-op if Git is missing or nothing changed."""
    try:
        if not is_repo():
            init()
            if not is_repo():
                return False
        _git("add", "-u")  # changed and deleted files already in the history
        _git("add", "-f", "--pathspec-from-file=-", stdin="\n".join(_personal_files()))
        if _git("diff", "--cached", "--quiet").returncode == 0:
            return False
        # Fresh Git installs have no name or email, and commit refuses without them.
        # This history is private, so a placeholder identity is fine.
        who = [] if _git("config", "user.email").stdout.strip() else ["-c", "user.name=learn", "-c", "user.email=learn@localhost"]
        return _git(*who, "commit", "-q", "-m", message).returncode == 0
    except FileNotFoundError:
        return False
