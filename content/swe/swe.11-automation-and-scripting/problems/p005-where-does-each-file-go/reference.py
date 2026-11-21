from pathlib import Path

CATEGORIES = {
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".pdf": "documents", ".docx": "documents", ".txt": "documents",
    ".csv": "data", ".xlsx": "data", ".json": "data",
    ".zip": "archives", ".tar": "archives", ".gz": "archives",
    ".mp3": "audio", ".wav": "audio",
}


def category_for(path):
    """The folder name for this file: by suffix, ignoring case; 'other' if unknown."""
    return CATEGORIES.get(Path(path).suffix.lower(), "other")


def unique_destination(dst):
    """dst if free, else 'stem (1)suffix', 'stem (2)suffix', ... (the first free one). Never creates anything."""
    dst = Path(dst)
    if not dst.exists():
        return dst
    n = 1
    while True:
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not candidate.exists():
            return candidate
        n += 1
