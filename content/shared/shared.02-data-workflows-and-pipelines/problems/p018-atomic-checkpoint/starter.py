import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("pipeline")


def save_checkpoint(path, state: dict) -> None:
    """Write state as JSON atomically: temp file in the same folder, then os.replace."""
    raise NotImplementedError("mkdir parents; json.dumps; write <name>.tmp; os.replace(tmp, path)")


def load_checkpoint(path, default: dict | None = None) -> dict:
    """Return the saved state; a copy of default if missing; quarantine a corrupt file."""
    raise NotImplementedError("missing -> copy of default; dict -> it; corrupt -> warn, move aside, default")
