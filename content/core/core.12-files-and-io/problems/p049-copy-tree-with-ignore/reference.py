import shutil
from pathlib import Path


def copy_project(src, dst, ignore=("__pycache__", "*.pyc", ".git"), overwrite=False):
    src = Path(src)
    dst = Path(dst)
    patterns = list(ignore)
    extra = src / ".copyignore"
    if extra.exists():
        for line in extra.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*patterns), dirs_exist_ok=overwrite)
    return sorted(p.relative_to(dst).as_posix() for p in dst.rglob("*") if p.is_file())
