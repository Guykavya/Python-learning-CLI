## Approach

Start everything, then react to finishing futures one at a time:

1. Submit every function to a pool with one worker per function, so they all start now.
2. Loop: `wait(pending, timeout=left, return_when=FIRST_COMPLETED)` returns when **at least
   one** future has finished. Look at each finished future:
   - `fut.exception() is None`: it succeeded, return `fut.result()`.
   - otherwise remember the error and keep going with the futures still in `pending`.
3. If `wait` returns an empty `done` set, the time ran out: raise `TimeoutError`.
4. If `pending` becomes empty, every function failed: raise `RuntimeError(...)` chained from
   the last error.

Two details make it fast:

- **A deadline, not a fresh timeout.** `deadline = time.monotonic() + timeout` is computed
  once; each `wait` gets `deadline - time.monotonic()`. Passing `timeout` every time would let
  a stream of failures push the end further and further away. `monotonic()` is used because
  it never jumps when the system clock is changed.
- **Do not wait for the losers.** `with ThreadPoolExecutor() as pool:` calls
  `shutdown(wait=True)` when the block ends, which waits for the slow mirror. Creating the
  pool without `with` and calling `shutdown(wait=False, cancel_futures=True)` in `finally`
  returns at once. Running threads still finish in the background (a thread cannot be
  killed), but queued jobs are cancelled and nobody waits for them.

## Code

```python
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait


def first_success(funcs, timeout):
    if not funcs:
        raise ValueError("need at least one function")
    deadline = time.monotonic() + timeout
    pool = ThreadPoolExecutor(max_workers=len(funcs))
    pending = {pool.submit(f) for f in funcs}
    last_error = None
    try:
        while pending:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError(f"no success within {timeout} s")
            done, pending = wait(pending, timeout=left, return_when=FIRST_COMPLETED)
            if not done:
                raise TimeoutError(f"no success within {timeout} s")
            for fut in done:
                err = fut.exception()
                if err is None:
                    return fut.result()
                last_error = err
        raise RuntimeError(f"all {len(funcs)} functions failed") from last_error
    finally:
        for fut in pending:
            fut.cancel()
        pool.shutdown(wait=False, cancel_futures=True)
```

`fut.exception()` does not block here: every future in `done` is already finished.

## Complexity

Wall time is the time of the first success (or of the last failure, or `timeout`), not the
sum of all times. Each `wait` call looks at the pending set, so the bookkeeping is O(n) per
finished future and O(n²) in the worst case, which is nothing for a handful of mirrors.

## Another way

`as_completed(futures, timeout=timeout)` gives the same loop: it yields futures in finishing
order and raises `TimeoutError` when the total time runs out (its timeout is already
measured from the call). Return on the first future whose `exception()` is `None`. You still
need the `shutdown(wait=False, cancel_futures=True)` trick so the losers are not waited for.

In asyncio the same pattern is `asyncio.wait(tasks, return_when=FIRST_COMPLETED)` in a loop,
and there you **can** cancel the losers for real with `task.cancel()`.
