# Stop the pool at the first error

A migration script runs 500 database steps on a thread pool. If one step fails, running the
other 499 is pointless (and may make a mess). It should **fail fast**: stop starting new work,
let the steps that are already running finish (a thread cannot be killed from outside), and
report what happened.

Write `run_until_error(funcs, workers) -> tuple[list, Exception | None]`:

- `funcs` is a list of zero-argument functions. Run them on a
  `concurrent.futures.ThreadPoolExecutor(max_workers=workers)`.
- As soon as **any** of them raises (the first failure to *complete*), cancel every function
  that has **not started yet**, so it never runs.
- Wait for the functions that were already running to finish, then return.
- Return `(results, error)`: `results` holds the return values of every function that finished
  **successfully**, in **input order**; `error` is the exception object that stopped the run,
  or `None` if nothing failed.

Do not leave any thread running after you return.

**Example** (2 workers)

```python
def ok(n, delay):  ...   # sleeps `delay`, returns n
def bad():          ...   # sleeps 0.1, raises ValueError("step 1 failed")

results, error = run_until_error([ok(0, 0.05), bad, ok(2, 0.2), ok(3, 0.05), ...20 more], 2)
# 0.05s: step 0 done, worker picks up step 2
# 0.10s: step 1 raises -> the 20 queued steps are cancelled
# 0.25s: step 2 (already running) finishes
results   # [0, 2]   (maybe also 3, if a worker grabbed it just before the cancel)
error     # ValueError('step 1 failed')
```

There is a small race in the last comment: the worker that ran the failing step is free at
the same instant, and it may pick up the next queued step before your code calls `cancel`.
That is fine, as long as that step's result is reported too and the rest never start.
