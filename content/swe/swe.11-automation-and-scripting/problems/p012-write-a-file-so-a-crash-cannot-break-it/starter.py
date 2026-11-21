import os
import tempfile
from pathlib import Path


def atomic_write_text(path, text):
    """Write text to path so a reader sees the old content or the new one, never half of it."""
    # TODO: temp file in the same folder, write + flush + os.fsync, os.replace; clean up and re-raise on failure
    Path(path).write_text(text, encoding="utf-8")
