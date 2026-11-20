## Hint 1

List the effects and where each one could be repeated or lost: the CSV file, the report status, the e-mail **job**, the e-mail itself. For each, which earlier problem already made it safe? (p025 for the file, p024 for "status + job together", p022 for the e-mail.)

## Hint 2

The order inside the report handler matters:

```text
validate month (permanent_error if bad)
rows = SELECT id, customer, total_cents FROM orders WHERE month = ?
write_atomic(path, build_report(rows, month), crash)       # crash points inside
crash.hit("report:after-replace")
with queue._connect() as db:
    BEGIN IMMEDIATE
    UPDATE reports SET status='ready', digest=? WHERE month=?
    queue.enqueue_in(db, "report_email", {"month": month}, dedupe_key=f"report-email:{month}")
    COMMIT   (ROLLBACK + raise on any BaseException)
crash.hit("report:after-status")
```

A rerun of the whole handler is harmless: the file gets identical bytes, the status is set to the same value, and the dedupe key stops a second e-mail job.

## Hint 3

For the API, the same "one transaction" pattern: `INSERT OR IGNORE` the report row and `enqueue_in` the report job with `dedupe_key=f"report:{month}"`, then read the row back for the status. Pydantic's `Field(pattern=MONTH_PATTERN)` gives the `422` for free.
