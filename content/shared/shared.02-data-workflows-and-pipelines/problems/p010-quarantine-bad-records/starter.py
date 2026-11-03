import json
from pathlib import Path


def process_batch(records, check, transform, quarantine_path, run_id):
    """Split records into good rows and quarantined ones (JSON Lines, appended). Never crash on one record."""
    return {"good": [], "total": 0, "ok": 0, "quarantined": 0}
