# An e-mail and report worker that survives crashes

Chapter section 16 (the project), built from your work in p018 (the queue), p021 (retries and dead letters), p022 (the idempotent e-mail handler), p024 (one transaction for a change and its job) and p025 (the deterministic, atomic report). This is the module's project in miniature.

## The rules (chapter 16.1)

1. Staff request a monthly report with `POST /reports` and get `202` at once. Asking for the same month twice creates **one** job. Invalid months are refused at the door (`422`).
2. A worker builds the report as CSV, **deterministically**, and publishes it **atomically**.
3. When the report is ready, finance gets **one** e-mail, whatever crashes or repeats.
4. Killing the worker at **any** moment loses nothing: after a restart the report exists and the e-mail went out exactly once.
5. A bad job goes to the dead state and does not block others. A job that keeps failing (provider down) ends dead and can be **redriven** after the outage.

## What you get

- `queue`: the chapter's `JobQueue` (section 9.2) on a fake clock. `queue.path` is the SQLite file, which also holds your tables. `queue._connect()` gives an autocommit connection with `row_factory = sqlite3.Row` (needed by `enqueue_in`). `queue.enqueue_in(db, kind, payload, dedupe_key=...)` enqueues **inside your transaction** on `db`. `queue.now()` is the time.
- `provider.send(to, subject, body, idempotency_key=None)`: the fake e-mail service (honours keys; may raise `ProviderTimeout` while it is down).
- `crash.hit(name)`: may raise `Crash` (the process dies). Never catch it.
- `permanent_error`: the worker's `PermanentError` class. Raise it for jobs that can never succeed.

## What to write

`SCHEMA`, `MONTH_PATTERN` and `init_db` are in the starter. Write:

```python
def build_report(rows, month) -> bytes: ...                 # as in p025
def write_atomic(path, data, crash) -> None: ...            # as in p025, crash points "report:mid-write", "report:before-replace"
def create_app(queue) -> FastAPI: ...
def make_handlers(queue, out_dir, provider, crash, permanent_error, recipient="finance@example.com") -> dict: ...
```

**`create_app(queue)`**

- `POST /reports` with JSON `{"month": "2026-10"}` (validate with `MONTH_PATTERN`, for example a Pydantic `Field(pattern=...)`): in **one transaction**, `INSERT OR IGNORE` a `reports` row (`status 'queued'`, `requested_at = queue.now()`) and `enqueue_in(db, "report", {"month": m}, dedupe_key=f"report:{m}")`. Answer `202` with `{"month": m, "status": <current status>, "status_url": f"/reports/{m}"}`.
- `GET /reports/{month}`: `{"month", "status", "digest"}`; `404` if unknown; `422` if the month is malformed.

**`make_handlers(...)`** returns `{"report": report_handler, "report_email": email_handler}`; each is called as `handler(payload, job)`.

- **report**: invalid month -> `raise permanent_error(...)`. Read the month's orders (`id, customer, total_cents`), `build_report`, `write_atomic` to `out_dir/report-<month>.csv`, then `crash.hit("report:after-replace")`. Then, in **one transaction**: set the report `status = 'ready'` and `digest` = the first 12 hex characters of the file's SHA-256, and `enqueue_in(db, "report_email", {"month": m}, dedupe_key=f"report-email:{m}")`. Then `crash.hit("report:after-status")`.
- **report_email**: p022's handler with key `report-ready:<month>`, sending to `recipient` with subject `f"Your report for {month} is ready"`. Crash points `"email:after-claim"`, `"email:after-send"`, `"email:after-record"`.

## Example

```text
POST /reports {"month": "2026-10"}   -> 202 {"month": "2026-10", "status": "queued", "status_url": "/reports/2026-10"}
(worker runs)
GET /reports/2026-10                 -> {"month": "2026-10", "status": "ready", "digest": "<12 hex>"}
out/report-2026-10.csv:
month,order_id,customer,total_cents
2026-10,1,ada,2500
2026-10,2,bo,4200
2026-10,3,cy,990
finance@example.com received one e-mail: "Your report for 2026-10 is ready"
```

## How it is tested: kill it everywhere

For each of the 7 crash points, a fresh world: request the report, run worker 1 until it dies at that point, then let time pass (leases expire) and drain with worker 2. The final state must equal a clean run: one e-mail, the exact CSV bytes, status `ready` with the right digest, every job `done`. More tests: duplicate report and e-mail jobs, a provider outage that ends `dead` and then a redrive, and a bad month next to a good one.

The chapter's version also runs as a real process killed with `SIGKILL` (section 16.4); that stays a "Try it on your machine".
