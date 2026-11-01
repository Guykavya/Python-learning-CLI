## Approach

1. **Submit everything.** `executor.submit` returns a `Future` per function at once; only
   `workers` of them run, the rest wait in the executor's queue.
2. **Watch completions.** `as_completed(futures)` yields each future when it finishes, fastest
   first. `future.exception()` on a finished future returns the exception (or `None`) instead
   of raising it, which makes the check easy. The first failure ends the loop.
3. **Stop the rest.** `executor.shutdown(wait=True, cancel_futures=True)` cancels every future
   that has not started and waits for the running threads. It is in a `finally`, so the pool is
   shut down even if something unexpected goes wrong in the loop.
4. **Collect in input order.** Walk the original `futures` list. Skip cancelled futures
   (calling `.exception()` or `.result()` on them raises `CancelledError`) and failed ones.

Why can a running function not be stopped? Python has no safe way to kill a thread: it might be
holding a lock or be half-way through writing a file. Cancellation in `concurrent.futures`
means "never start". (If long-running steps must stop early, pass them a `threading.Event` to
check now and then, as in p009.)

The race in the problem statement: the worker that ran the failing step finishes it, then
immediately takes the next queued item, while the main thread is only *starting* to wake up
from `as_completed`. So one extra step may start. The tests allow that and only require that
its result is reported if it succeeds.

## Code

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_until_error(funcs, workers):
    executor = ThreadPoolExecutor(max_workers=workers)
    futures = [executor.submit(func) for func in funcs]
    error = None
    try:
        for future in as_completed(futures):
            if future.exception() is not None:
                error = future.exception()
                break
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
    results = [
        future.result()
        for future in futures
        if not future.cancelled() and future.exception() is None
    ]
    return results, error
```

## Complexity

n submissions, O(n) work to collect. Without a failure, wall time is about the total work
divided by `workers`; with one, it is the time to the first failure plus the longest step that
was already running.

## Another way

Use `concurrent.futures.wait(futures, return_when=FIRST_EXCEPTION)`: it returns `(done,
not_done)` when the first future fails (or when all are done). Then cancel each future in
`not_done` with `future.cancel()` (those already running return `False` and carry on), and let
a `with` block's exit wait for them. It is the same idea in a different shape; `as_completed`
also gives you a natural place to report progress.
