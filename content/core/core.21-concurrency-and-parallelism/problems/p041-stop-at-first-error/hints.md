## Hint 1

You need the futures in two orders: **completion** order to notice the first failure as soon
as it happens, and **input** order to build `results`. Which function yields futures as they
finish? And how do you ask a finished future "did you fail?" without it raising at you?

## Hint 2

A future can be cancelled only while it is still **queued**; `cancel()` on a running one
returns `False`. `executor.shutdown(wait=True, cancel_futures=True)` cancels every queued
future and then waits for the running ones. Careful: leaving a `with ThreadPoolExecutor()`
block calls `shutdown(wait=True)` **without** `cancel_futures`, so the queued work still runs.

```
executor = ThreadPoolExecutor(workers)
futures = [executor.submit(f) for f in funcs]
error = None
try:
    for fut in as_completed(futures):
        if fut.exception() is not None:
            error = fut.exception(); break
finally:
    executor.shutdown(wait=True, cancel_futures=True)
results = [fut.result() for fut in futures
           if not fut.cancelled() and fut.exception() is None]
```
