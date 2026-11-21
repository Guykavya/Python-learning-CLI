import os
import tempfile
from pathlib import Path


def atomic_write_text(path, text):
    """Write text to path so a reader sees the old content or the new one, never half of it."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())               # make sure the bytes reached the disk
        os.replace(tmp, path)                  # atomic on the same file system
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
