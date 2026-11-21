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
    clock = clock or (lambda: datetime.now(timezone.utc))
    Path(status_dir).mkdir(parents=True, exist_ok=True)
    start = clock()
    status = {"job": name, "start": start.isoformat()}
    log.info("job %s starting", name)
    try:
        status.update(ok=True, result=fn(), error=None)
        code = 0
    except Exception as e:
        log.error("job %s failed: %s", name, e)
        status.update(ok=False, result=None, error=f"{type(e).__name__}: {e}")
        code = 1
    status["end"] = clock().isoformat()
    write_json_atomic(Path(status_dir) / f"{name}.json", status)
    return code


def problem_with(status_file, max_age_hours, now):
    """'never ran', 'failed', 'stale' or None."""
    path = Path(status_file)
    if not path.exists():
        return "never ran"
    status = json.loads(path.read_text(encoding="utf-8"))
    if not status["ok"]:
        return "failed"
    if now - datetime.fromisoformat(status["end"]) > timedelta(hours=max_age_hours):
        return "stale"
    return None
