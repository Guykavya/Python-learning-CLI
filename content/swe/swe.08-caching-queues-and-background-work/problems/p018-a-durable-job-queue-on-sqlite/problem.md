# A durable job queue on SQLite

Chapter sections 9.1 to 9.4 (building a durable job queue). Build the queue yourself: jobs are rows in a SQLite file, so they survive a restart; a worker **reserves** a job with a **lease**; if the worker dies, the lease runs out and the job comes back. The table is given in the starter (it is the chapter's table without the `queue` column).

## What to write

```python
class JobQueue:
    def __init__(self, path, now=time.time): ...      # create the table if needed
    def enqueue(self, kind, payload, *, delay=0.0, max_attempts=5, dedupe_key=None) -> int: ...
    def reserve(self, worker, *, lease=30.0) -> dict | None: ...
    def complete(self, job_id, worker) -> bool: ...
    def fail(self, job, error, *, retry_in=0.0, permanent=False) -> bool: ...
    def get(self, job_id) -> dict | None: ...
```

| Method | Rules |
|---|---|
| `enqueue` | stores `payload` as JSON text (`json.dumps(payload, sort_keys=True)`), `run_at = now + delay`, `created_at = now`. With a `dedupe_key` that already exists, **no new job** is made and the existing job's id is returned. |
| `reserve` | picks the **ready** job with the smallest `(run_at, id)` and claims it **in one statement**: `state='running'`, `attempts + 1`, `lease_until = now + lease`, `worker = worker`. A job is ready if it is `queued` with `run_at <= now`, **or** `running` with `lease_until <= now` (its worker died). Returns the row as a dict (after the update), or `None`. |
| `complete` | sets `state='done'`, `finished_at=now`, `lease_until=NULL` **only if** the job is `running` and held by this `worker`. Returns whether a row changed. |
| `fail` | if `permanent` or `job["attempts"] >= job["max_attempts"]`: `state='dead'`, `finished_at=now`. Otherwise `state='queued'`, `run_at = now + retry_in`. Both store `last_error=error`, set `lease_until=NULL`, and apply only if the job is still `running` and held by `job["worker"]`. Returns whether a row changed. |
| `get` | the row as a dict, or `None`. |

Open a **new connection per call** (`sqlite3.connect(path, timeout=10, isolation_level=None)`, `row_factory = sqlite3.Row`), so each statement commits on its own, and close it (`contextlib.closing`).

"In one statement" for `reserve` is the heart of it (chapter 9.2):

```sql
UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?, worker = ?
WHERE id = (SELECT id FROM jobs WHERE (state = 'queued' AND run_at <= ?) OR (state = 'running' AND lease_until <= ?)
            ORDER BY run_at, id LIMIT 1)
RETURNING *
```

`RETURNING` needs SQLite 3.35 or newer (Python 3.11 ships with a newer one).

## Example

```python
q = JobQueue("q.db", now=clock)
q.enqueue("email", {"to": "ada"})                 # 1
q.enqueue("email", {"to": "bo"}, delay=60)        # 2
job = q.reserve("w1")                             # job 1: state 'running', attempts 1
json.loads(job["payload"])                        # {'to': 'ada'}
q.reserve("w1")                                   # None: job 2 is not due yet
q.complete(job["id"], "w2")                       # False: w2 does not hold it
q.complete(job["id"], "w1")                       # True
```

The tests use a fake clock and a file in a temporary folder.
