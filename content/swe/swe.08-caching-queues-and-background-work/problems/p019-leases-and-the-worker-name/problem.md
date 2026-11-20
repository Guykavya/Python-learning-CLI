# Leases and the worker name

Chapter sections 9.3 (a crash and a lease), 9.5 (many workers, no double claims) and "Try it: why check the worker name?". Write the three statements that make a job queue safe with many workers. Each function receives an open SQLite connection `db` (autocommit, `row_factory = sqlite3.Row`) to this table:

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}',
    state TEXT NOT NULL DEFAULT 'queued',      -- queued, running, done, dead
    attempts INTEGER NOT NULL DEFAULT 0, run_at REAL NOT NULL DEFAULT 0,
    lease_until REAL, worker TEXT
);
```

## What to write

```python
def reserve(db, worker, now, lease=30.0) -> dict | None: ...
def complete(db, job_id, worker, now) -> bool: ...
def heartbeat(db, job_id, worker, now, lease=30.0) -> bool: ...
```

`now` is a number (seconds), not a function.

- `reserve`: claim the ready job with the smallest `(run_at, id)`: set `state='running'`, `attempts + 1`, `lease_until = now + lease`, `worker = worker`, and return the updated row as a dict (or `None`). Ready means `queued` with `run_at <= now`, **or** `running` with `lease_until <= now`. **Two workers must never claim the same job**, even when they call `reserve` at the same moment.
- `complete`: mark the job `done` and clear `lease_until`, **only if** it is `running` and its `worker` is this worker. Return whether a row changed.
- `heartbeat`: a long job calls this to extend its lease to `now + lease`, again **only if** it still holds the job. `False` tells the worker "you lost this job, stop".

## Example

```python
a = connect(); b = connect()
reserve(a, "worker-A", now=0, lease=30)       # {'id': 1, 'state': 'running', 'attempts': 1, ...}
reserve(b, "worker-B", now=10)                # None: leased to A
reserve(b, "worker-B", now=31)                # job 1 again, attempts 2: A's lease ran out
complete(a, 1, "worker-A", now=32)            # False: A no longer owns it
complete(b, 1, "worker-B", now=33)            # True
```

One test gives each worker a connection whose `SELECT` statements are slow (20 ms), and starts 4 workers at once. A version that first `SELECT`s the next id and then `UPDATE`s it by id lets two workers claim the same job. Claim in **one** statement (chapter 9.2), or make the `UPDATE` check that the row is still claimable and look at `rowcount`.
