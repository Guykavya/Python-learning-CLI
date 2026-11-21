## Approach

```python
def missed_days(last_success, now):
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
    done = []
    for day in missed_days(_read_state(state_path), now):
        try:
            job(day)
        except Exception:
            return done, day
        done.append(day)
        write_json_atomic(state_path, {"last_success": day.isoformat()})
    return done, None
```

Three ideas from section 13.3 make the job self-repairing. The work is **keyed by date** ("the report for 19 November"), so it can be built late. **Progress is recorded** after every day, atomically, so a crash or a failure loses at most the day in progress. And it **stops at the first failure** in order, so days are never skipped: the state never claims a day that was not done, and the next run starts exactly where this one failed.

## Complexity

O(d) job calls and state writes for d missed days.

## Another way

Cap the catch-up (`days[-31:]`, or refuse with an alert when more than a month is missing): after a long outage, 300 reports at once might hit an API's rate limit or fill a mailbox, and a human should decide. Also make `job(day)` itself idempotent (write the report to `reports/2026-11-19.csv` with an atomic replace), so even a rerun of a done day would be harmless.
