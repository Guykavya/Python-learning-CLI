import json
import os
import tempfile
from datetime import date, timedelta
from pathlib import Path


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


def missed_days(last_success, now):
    """Days after last_success up to and including now.date(); [today] if last_success is None."""
    today = now.date()
    if last_success is None:
        return [today]
    days, day = [], last_success + timedelta(days=1)
    while day <= today:
        days.append(day)
        day += timedelta(days=1)
    return days


def _read_state(state_path):
    path = Path(state_path)
    if not path.exists():
        return None
    return date.fromisoformat(json.loads(path.read_text(encoding="utf-8"))["last_success"])


def run_daily(job, state_path, now):
    """Run job(day) for each missed day, oldest first; save progress after each; stop at the first failure."""
    done = []
    for day in missed_days(_read_state(state_path), now):
        try:
            job(day)
        except Exception:
            return done, day
        done.append(day)
        write_json_atomic(state_path, {"last_success": day.isoformat()})
    return done, None
