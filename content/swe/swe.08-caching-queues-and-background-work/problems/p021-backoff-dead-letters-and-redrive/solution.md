## Approach

The queue already knows how to bury a job whose attempts are used up; the worker's job is to classify the error, pick the delay, and report the outcome. The operator tools read and reset rows.

```python
def backoff_delay(attempt, base=2.0, cap=300.0, rng=random.random):
    delay = min(cap, base * 2 ** (attempt - 1))
    return delay / 2 + rng() * delay / 2


def process_one(queue, handler, worker, *, permanent=(), base=2.0, cap=300.0, rng=random.random):
    job = queue.reserve(worker)
    if job is None:
        return None
    try:
        handler(json.loads(job["payload"]))
    except Exception as exc:
        text = f"{type(exc).__name__}: {exc}"
        if isinstance(exc, permanent):
            return "dead" if queue.fail(job, text, permanent=True) else "lease-lost"
        if not queue.fail(job, text, retry_in=backoff_delay(job["attempts"], base, cap, rng)):
            return "lease-lost"
        return "dead" if queue.get(job["id"])["state"] == "dead" else "retry"
    return "done" if queue.complete(job["id"], worker) else "lease-lost"


def dead_letters(queue):
    with closing(sqlite3.connect(queue.path)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT id, kind, attempts, last_error FROM jobs WHERE state = 'dead' ORDER BY id")
        return [dict(row) for row in rows]


def redrive(queue, job_id):
    return queue.requeue_dead(job_id)


def redrive_all(queue, limit=None):
    jobs = dead_letters(queue)
    if limit is not None:
        jobs = jobs[:limit]
    return sum(1 for job in jobs if redrive(queue, job["id"]))
```

## Cost

Each processed job costs a reserve, the handler and one or two updates. Backoff with equal jitter spreads retries: after an outage that failed 10,000 jobs at the same second, their retries arrive over a window of half the delay instead of in one spike.

## Another way

**Full jitter** (`rng() * delay`) spreads retries even more but can retry almost at once; **decorrelated jitter** grows from the previous delay. A real system also adds a **circuit breaker** (chapter 12.2) so that an outage does not burn every job's attempts, and an alert when the dead-letter count grows.
