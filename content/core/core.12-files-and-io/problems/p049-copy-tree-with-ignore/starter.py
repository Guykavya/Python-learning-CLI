import shutil
from pathlib import Path


def copy_project(src, dst, ignore=("__pycache__", "*.pyc", ".git"), overwrite=False):
    # TODO: patterns = ignore + lines of src/.copyignore; shutil.copytree(..., ignore=shutil.ignore_patterns(...))
    return None
