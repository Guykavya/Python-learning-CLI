import json
import logging
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

log = logging.getLogger("auto.job")


def write_json_atomic(path, data):
    """Given (chapter 13.1): write JSON so a reader sees the old file or the new one, never half."""
    fd, tmp = tempfile.mkstemp(dir=Path(path).parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def run_job(name, fn, status_dir, clock=None):
    """Run fn(), always record the outcome in <status_dir>/<name>.json, return 0 (ok) or 1 (failed)."""
    # TODO
    return 0


def problem_with(status_file, max_age_hours, now):
    """'never ran', 'failed', 'stale' or None."""
    # TODO
    return None
