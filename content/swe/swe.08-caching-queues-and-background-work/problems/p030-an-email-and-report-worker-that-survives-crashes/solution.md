## Approach

Every step is made safe by a tool from an earlier problem:

| Step | Crash or repeat after it | Defence |
|---|---|---|
| API: report row + job | a double click, a retried request | one transaction; `dedupe_key = report:<month>` |
| build the CSV | rerun | deterministic bytes (sorted, no clock) |
| write the file | crash mid-write / before rename | `.tmp` + `fsync` + `os.replace` |
| status + e-mail job | crash between them | one transaction (outbox idea) |
| rerun of the report job | a second e-mail job | `dedupe_key = report-email:<month>` |
| e-mail | crash after send, lost response, duplicate job | log + provider idempotency key `report-ready:<month>` |
| provider down | attempts used up | backoff, `dead` with the last error, redrive after the outage |
| invalid month | retry for ever | `permanent_error`: dead at once |

The full code is `reference.py`. The heart of it:

```python
def report(payload, job):
    month = payload.get("month", "")
    if not re.match(MONTH_PATTERN, month):
        raise permanent_error(f"invalid month {month!r}")
    with closing(sqlite3.connect(queue.path, isolation_level=None)) as db:
        rows = [tuple(r) for r in db.execute("SELECT id, customer, total_cents FROM orders WHERE month = ?", (month,))]
    path = os.path.join(out_dir, f"report-{month}.csv")
    write_atomic(path, build_report(rows, month), crash)
    crash.hit("report:after-replace")
    file_digest = digest(path)
    with closing(queue._connect()) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute("UPDATE reports SET status = 'ready', digest = ? WHERE month = ?", (file_digest, month))
            queue.enqueue_in(db, "report_email", {"month": month}, dedupe_key=f"report-email:{month}")
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    crash.hit("report:after-status")
```

## Cost

Per report: one query, one file written twice (temporary + rename), two small transactions, one e-mail with a log row. The crash test matrix runs 7 crash points plus the other scenarios in about a second and a half (machine-specific), which is cheap enough to run on every change.

## Another way

The chapter (16.3 to 16.5) runs the worker as a real **process** and kills it with `SIGKILL`, using an `EnvCrash` hook that calls `os._exit(137)` and a provider whose memory is a SQLite file (an in-memory fake would "forget" when the process dies). Try it on your machine with `worker_main.py`. In production you would also add a heartbeat for long reports, metrics on queue age and dead-letter count, and graceful shutdown on `SIGTERM` (chapter 10.2 and 15).
