## Approach

| Job | Runs at | What happens | Final |
|---|---|---|---|
| a | 0 | success -> `complete` | done, 1, 0.0 |
| b | 0 | `RetryLater(delay=45)` -> run_at = 0 + 45 | queued, 1, 45.0 |
| c | 0 | `PermanentError` -> dead at once | dead, 1, 0.0 |
| d | 0 | `KeyError` (unexpected, so treated as temporary) -> backoff(1) = 1.5 | queued, 1, 1.5 |
| e | 0, 1000, 2000 | `TimeoutError` three times; third failure: backoff(3) = 6 -> 2000 + 6 | queued, 3, 2006.0 |
| f | 0 ... 4000 | 4th failure at 3000: backoff(4) = 12 -> 3012; 5th attempt at 4000 reaches max_attempts -> dead, run_at unchanged | dead, 5, 3012.0 |

Lessons: a `KeyError` from a bad payload is retried as if it were temporary (to make it permanent, validate the payload and raise `PermanentError`); attempts are counted when a job is **reserved**; a dead job keeps the `run_at` of its last retry, so `finished_at` is the field that says when it died.

## Cost

Reading only. The backoff table is worth memorising: with base 2 s and 5 attempts, a job is dead after about 30 seconds of waits at most, far too short for a provider outage (chapter "Try it: size the policy").

## Another way

Paste the chapter's `jobqueue.py` and `worker.py` into a folder in `playground/`, save the program as a file next to them, and run it. Then change `max_attempts` to 3 for job `f` and predict the line before running.
