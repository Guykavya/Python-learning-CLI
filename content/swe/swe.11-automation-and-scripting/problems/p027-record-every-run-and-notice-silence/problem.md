# Record every run, and notice silence

Chapter sections 13.1 (one wrapper that records every run) and 13.2 (get told: alerts and the dead-man's switch). An unattended job fails in boring ways, and the danger is that **nobody notices**. Two small functions fix that: a wrapper that runs a job and always writes a **status file**, and a checker that reads it and says what is wrong, including the failure that cannot report itself: the job **did not run at all**.

## What to write

The starter gives `write_json_atomic(path, data)` (section 13.1) and a logger `log`. Write:

```python
def run_job(name, fn, status_dir, clock=None) -> int: ...
def problem_with(status_file, max_age_hours, now) -> str | None: ...
```

`run_job(name, fn, status_dir, clock=None)`:
- `clock` is a function that returns the current time as a timezone-aware `datetime`; `None` means `lambda: datetime.now(timezone.utc)`. Call it exactly **twice**: once before `fn()` (start) and once after (end). The tests pass a fake clock, so durations and ages are exact.
- creates `status_dir` if needed, runs `fn()` and **always** writes `<status_dir>/<name>.json` with `write_json_atomic`, containing:
  `{"job": name, "start": <iso>, "end": <iso>, "ok": true/false, "result": <what fn returned, or null>, "error": null or "<ExceptionType>: <message>"}` (times with `.isoformat()`);
- returns `0` if `fn` returned, `1` if it raised an `Exception`; the exception is **not** re-raised (the exit code and the status file tell the story), but it is logged with `log.error` including the job name.

`problem_with(status_file, max_age_hours, now)` (the dead-man's switch; `now` is a `datetime`):
- `"never ran"` if the file does not exist;
- `"failed"` if the last run has `"ok": false`;
- `"stale"` if the last run ended **more than** `max_age_hours` before `now` (exactly at the limit is still fine);
- `None` if everything looks healthy.

## Example

```python
t0 = datetime(2026, 11, 21, 3, 0, tzinfo=timezone.utc)
ticks = iter([t0, t0 + timedelta(seconds=4)])
run_job("tidy", lambda: {"files_moved": 12}, "status", clock=lambda: next(ticks))     # 0
# status/tidy.json: {"job": "tidy", "start": "2026-11-21T03:00:00+00:00", "end": "2026-11-21T03:00:04+00:00",
#                    "ok": true, "result": {"files_moved": 12}, "error": null}
problem_with("status/tidy.json", 24, now=t0 + timedelta(hours=10))     # None
problem_with("status/tidy.json", 24, now=t0 + timedelta(days=2))       # 'stale'
problem_with("status/report.json", 24, now=t0)                         # 'never ran'
```
