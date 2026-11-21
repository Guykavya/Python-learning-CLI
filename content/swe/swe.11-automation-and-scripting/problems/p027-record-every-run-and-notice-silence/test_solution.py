import json
import logging
from datetime import datetime, timedelta, timezone

import pytest

from solution import problem_with, run_job

T0 = datetime(2026, 11, 21, 3, 0, tzinfo=timezone.utc)


def clock_of(*times):
    ticks = iter(times)
    return lambda: next(ticks)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_success_is_recorded(tmp_path):
    status_dir = tmp_path / "status"
    code = run_job("tidy", lambda: {"files_moved": 12}, status_dir, clock=clock_of(T0, T0 + timedelta(seconds=4)))
    assert code == 0, "A job that returns normally gives exit code 0."
    data = read(status_dir / "tidy.json")
    assert data == {"job": "tidy", "start": "2026-11-21T03:00:00+00:00", "end": "2026-11-21T03:00:04+00:00",
                    "ok": True, "result": {"files_moved": 12}, "error": None}, \
        f"Status file fields: job, start, end (isoformat of the clock's two times), ok, result, error. Got {data}"


def test_failure_is_recorded_and_not_raised(tmp_path, caplog):
    def bad():
        raise ConnectionError("backup server unreachable")

    with caplog.at_level(logging.ERROR):
        code = run_job("backup", bad, tmp_path, clock=clock_of(T0, T0 + timedelta(seconds=1)))
    assert code == 1, "A job that raises gives exit code 1 (and run_job does not re-raise)."
    data = read(tmp_path / "backup.json")
    assert data["ok"] is False and data["result"] is None
    assert data["error"] == "ConnectionError: backup server unreachable", f"error is '<Type>: <message>'; got {data['error']!r}"
    assert data["end"] == "2026-11-21T03:00:01+00:00", "The end time is recorded for failures too."
    assert any("backup" in r.getMessage() and "unreachable" in r.getMessage() for r in caplog.records), \
        "Log the failure with log.error, naming the job and the error."


def test_clock_is_called_twice(tmp_path):
    calls = []

    def clock():
        calls.append(1)
        return T0

    run_job("x", lambda: None, tmp_path, clock=clock)
    assert len(calls) == 2, f"Call the clock once for start and once for end; it was called {len(calls)} times."


def test_status_dir_is_created_and_no_temp_files(tmp_path):
    status_dir = tmp_path / "deep" / "status"
    run_job("a", lambda: 1, status_dir, clock=clock_of(T0, T0))
    run_job("a", lambda: 2, status_dir, clock=clock_of(T0, T0))
    assert sorted(p.name for p in status_dir.iterdir()) == ["a.json"], "Create the folder; write atomically; leave no temp files."
    assert read(status_dir / "a.json")["result"] == 2, "Each run replaces the previous status."


def test_default_clock_is_utc(tmp_path):
    run_job("now", lambda: None, tmp_path)
    start = datetime.fromisoformat(read(tmp_path / "now.json")["start"])
    assert start.tzinfo is not None, "Without a clock, use datetime.now(timezone.utc): aware times."


def test_never_ran(tmp_path):
    assert problem_with(tmp_path / "report.json", 24, now=T0) == "never ran"


def test_failed(tmp_path):
    run_job("backup", lambda: 1 / 0, tmp_path, clock=clock_of(T0, T0))
    assert problem_with(tmp_path / "backup.json", 24, now=T0) == "failed"


def test_healthy_and_stale(tmp_path):
    run_job("tidy", lambda: None, tmp_path, clock=clock_of(T0, T0 + timedelta(minutes=1)))
    f = tmp_path / "tidy.json"
    assert problem_with(f, 24, now=T0 + timedelta(hours=10)) is None, "Ten hours old with a 24-hour limit is healthy."
    assert problem_with(f, 24, now=T0 + timedelta(days=2)) == "stale", "Two days without a run: the dead-man's switch fires."


def test_limit_is_measured_from_the_end_and_is_inclusive(tmp_path):
    end = T0 + timedelta(minutes=30)
    run_job("tidy", lambda: None, tmp_path, clock=clock_of(T0, end))
    f = tmp_path / "tidy.json"
    assert problem_with(f, 24, now=end + timedelta(hours=24)) is None, "Exactly 24 hours after the end is not MORE than 24 hours."
    assert problem_with(f, 24, now=end + timedelta(hours=24, seconds=1)) == "stale"


def test_failed_wins_over_stale(tmp_path):
    run_job("backup", lambda: 1 / 0, tmp_path, clock=clock_of(T0, T0))
    assert problem_with(tmp_path / "backup.json", 24, now=T0 + timedelta(days=9)) == "failed", \
        "A failed last run is reported as 'failed' even when it is also old."
