# Catch up after downtime

Chapter sections 13.3 (idempotent jobs and catching up: key the work by date, record progress) and 13.4 (retries and limits). Cron skips a job when the machine is off. A daily report job written as "make the report for *today*" silently loses those days. Written as "make the report for **each day since the last success**", the next run repairs the gap by itself.

## What to write

The starter gives `write_json_atomic`. Write:

```python
def missed_days(last_success, now) -> list[date]: ...
def run_daily(job, state_path, now) -> tuple[list[date], date | None]: ...
```

`missed_days(last_success, now)`:
- `last_success` is a `date` or `None`; `now` is a `datetime`; "today" is `now.date()`;
- returns every day **after** `last_success` up to and **including** today, in order;
- `None` (the job has never succeeded) means only `[today]`: a brand-new job does not invent a backlog;
- if `last_success` is today or later, returns `[]`.

`run_daily(job, state_path, now)`:
- reads the state file (JSON `{"last_success": "2026-11-17"}`); a missing file means `None`;
- calls `job(day)` for each missed day, **oldest first**;
- after **each** successful day, saves the new state at once (atomically), so progress survives a crash in a later day;
- stops at the **first** day whose `job(day)` raises an `Exception`, and does not run the later days (they would be built on a missing day). The state keeps the last successful day, so the next call starts again **at the failed day**;
- returns `(days_done, failed_day)`, where `failed_day` is `None` when everything went well.

Running it twice with the same `now` does nothing the second time (idempotent): the state already says today is done.

## Example

```python
# state: {"last_success": "2026-11-17"}, the machine was off for three days
run_daily(make_report, "state.json", now=datetime(2026, 11, 21, 8, 0))
# make_report(2026-11-18), (11-19), (11-20), (11-21)  ->  ([18, 19, 20, 21 Nov], None)
run_daily(make_report, "state.json", now=datetime(2026, 11, 21, 9, 0))
# ([], None)                     nothing left to do
# if make_report(11-19) had raised: ([18 Nov], 19 Nov), state = 2026-11-18, next run starts at the 19th
```
