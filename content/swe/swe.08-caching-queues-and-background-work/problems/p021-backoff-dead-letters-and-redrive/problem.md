# Backoff, dead letters and redrive

Chapter sections 10.1 (the worker loop), 12.1 (a retry policy) and 12.3 (dead letters). You receive the chapter's `JobQueue` (section 9.2) as `queue`. Write the retry side of a worker and the operator tools for the dead-letter "inbox".

## What to write

```python
def backoff_delay(attempt, base=2.0, cap=300.0, rng=random.random) -> float: ...
def process_one(queue, handler, worker, *, permanent=(), base=2.0, cap=300.0, rng=random.random) -> str | None: ...
def dead_letters(queue) -> list[dict]: ...
def redrive(queue, job_id) -> bool: ...
def redrive_all(queue, limit=None) -> int: ...
```

- **`backoff_delay`**: exponential backoff with **equal jitter** (chapter 10.1): `delay = min(cap, base * 2 ** (attempt - 1))`, return `delay / 2 + rng() * delay / 2`. `attempt` starts at 1.
- **`process_one`**: reserve one job with `queue.reserve(worker)`; if there is none, return `None`. Call `handler(payload)` with the payload **decoded from JSON**.
  - success -> `queue.complete(job["id"], worker)`; return `"done"`.
  - an exception that is an instance of one of the `permanent` types -> `queue.fail(job, text, permanent=True)`; return `"dead"`.
  - any other `Exception` -> `queue.fail(job, text, retry_in=backoff_delay(job["attempts"], base, cap, rng))`; return `"dead"` if the job ended in the dead state (the queue buries it when attempts are used up), else `"retry"`.
  - `text` is `f"{type(exc).__name__}: {exc}"`, e.g. `"ConnectionError: provider down"`.
  - if `complete` or `fail` returns `False` (the lease was lost), return `"lease-lost"`.
- **`dead_letters`**: every dead job as `{"id", "kind", "attempts", "last_error"}`, ordered by id. `queue.path` is the SQLite file (`sqlite3.connect(queue.path)`).
- **`redrive`**: put one dead job back with `queue.requeue_dead(job_id)` (attempts reset to 0, ready now). `False` if the job is not dead.
- **`redrive_all`**: redrive the dead jobs in id order, at most `limit` of them (all when `None`); return how many. Operators redrive **a few first** to check the fix works.

## Example

```python
jid = queue.enqueue("email", {"to": "ada"}, max_attempts=3)
process_one(queue, flaky, "w1", rng=lambda: 0.5)   # 'retry'   run_at = 0 + 1.5
clock.advance(100); process_one(...)                # 'retry'   attempt 2: run_at = 100 + 3.0
clock.advance(100); process_one(...)                # 'dead'    attempt 3 = max_attempts
dead_letters(queue)    # [{'id': 1, 'kind': 'email', 'attempts': 3, 'last_error': 'ConnectionError: provider down'}]
redrive(queue, jid)    # True
```

Redriving is safe **only if the handler is idempotent**: a job in the dead state may have partly run. Problem p022 builds such a handler.
