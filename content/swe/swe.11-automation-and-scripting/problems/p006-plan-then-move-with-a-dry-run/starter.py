import json
import shutil
from pathlib import Path

CATEGORIES = {
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".pdf": "documents", ".docx": "documents", ".txt": "documents",
    ".csv": "data", ".xlsx": "data", ".json": "data",
    ".zip": "archives", ".tar": "archives", ".gz": "archives",
    ".mp3": "audio", ".wav": "audio",
}
JOURNAL = ".tidy-journal.json"


def category_for(path):
    return CATEGORIES.get(Path(path).suffix.lower(), "other")


def unique_destination(dst):
    """Never overwrite: if 'a.txt' exists, use 'a (1).txt', 'a (2).txt'..."""
    if not dst.exists():
        return dst
    n = 1
    while True:
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def plan_moves(root):
    """Decide what to move where. Changes nothing. Only files directly in `root`, no hidden ones."""
    # TODO
    return []


def apply_moves(moves, root, dry_run=False):
    """Do the moves (unless dry_run) and write a journal so they can be undone."""
    # TODO
    return []
