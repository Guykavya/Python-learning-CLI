import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("pipeline")


def save_checkpoint(path, state: dict) -> None:
    """Write state as JSON atomically: temp file in the same folder, then os.replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(state, ensure_ascii=False, indent=2)   # TypeError here: nothing touched yet
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())               # make sure the bytes are on disk before the rename
    os.replace(tmp, path)                  # atomic: old file or new file, never half of one


def load_checkpoint(path, default: dict | None = None) -> dict:
    """Return the saved state; a copy of default if missing; quarantine a corrupt file."""
    path = Path(path)
    fallback = dict(default) if default is not None else {}
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return fallback
    except UnicodeDecodeError:
        text = None
    try:
        state = json.loads(text) if text is not None else None
    except ValueError:
        state = None
    if isinstance(state, dict):
        return state
    corrupt = path.with_name(path.name + ".corrupt")
    os.replace(path, corrupt)
    logger.warning("checkpoint %s is corrupt; moved to %s, starting from the default", path, corrupt.name)
    return fallback
