# What happens to the job?

Chapter sections 9.2 (the queue), 10.1 (the worker loop) and "Try it: classify the error". Below, six jobs each meet a different handler. Each job gets its own fresh queue and runs through the chapter's `Worker` (section 10.1) with the chapter's `JobQueue` (section 9.2). You do not need to run them: the rules are listed after the program.

```python
import os
import tempfile

from jobqueue import JobQueue
from worker import PermanentError, RetryLater, Worker


def ok(payload, job):
    pass


def rate_limited(payload, job):
    raise RetryLater("rate limited", delay=45)


def bad_payload(payload, job):
    raise PermanentError("order_id is not a number")


def missing_field(payload, job):
    return payload["order_id"]                     # KeyError: the payload is {}


def slow_provider(payload, job):
    raise TimeoutError("provider did not answer")


CASES = [            # (label, handler, how many times the worker runs)
    ("a", ok, 1),
    ("b", rate_limited, 1),
    ("c", bad_payload, 1),
    ("d", missing_field, 1),
    ("e", slow_provider, 3),
    ("f", slow_provider, 5),
]

with tempfile.TemporaryDirectory() as tmp:
    for label, handler, runs in CASES:
        clock = [0.0]
        q = JobQueue(os.path.join(tmp, f"{label}.db"), now=lambda: clock[0])
        w = Worker(q, {"task": handler}, rng=lambda: 0.5)
        job_id = q.enqueue("task", {}, max_attempts=5)
        for run in range(runs):
            if run > 0:
                clock[0] += 1000                   # long enough for any retry delay
            w.run_once()
        job = q.get(job_id)
        print(f"{label}: {job['state']} attempts={job['attempts']} run_at={job['run_at']}")
```

## The rules you need

- `reserve` counts the attempt: `attempts + 1` when the job is claimed.
- `Worker.run_once` catches the handler's exception:
  - `PermanentError` -> `fail(..., permanent=True)`: state `dead`, `run_at` unchanged.
  - `RetryLater(delay=45)` -> `fail(..., retry_in=45)`.
  - any other `Exception` -> `fail(..., retry_in=backoff_delay(attempts, rng=...))`.
  - no exception -> `complete`: state `done`.
- `fail` makes the job `dead` instead of `queued` when `attempts >= max_attempts` (here 5); then `run_at` is **not** changed.
- A retry sets `run_at = now + retry_in`.
- `backoff_delay(attempt, base=2.0, cap=300.0, rng)`: `delay = min(cap, base * 2 ** (attempt - 1))`, returns `delay / 2 + rng() * delay / 2`. With `rng()` = 0.5 that is `0.75 * delay`.
- Every run after the first happens 1000 seconds later than the previous one, which is after any retry delay here.
- `run_at` is a float, printed by Python as `45.0`, `2006.0`, ...

## What to write

The exact six lines of output.

## Example

Job `a` succeeds on its first run: `a: done attempts=1 run_at=0.0`.
