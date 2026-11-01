## Approach

`asyncio.wait(tasks, timeout=t)` is the right tool because it does **not** treat the timeout
as an error and does **not** cancel anything: it returns `(done, pending)` after `t` seconds,
or earlier if everything finished. What to do with `pending` is our decision.

**Cancel, then await.** `task.cancel()` only *schedules* a `CancelledError` to be thrown into
the task the next time it runs. Its `except` and `finally` blocks have not run yet, and if the
`finally` itself awaits (closing a connection), it needs several more turns of the event loop.
`await asyncio.gather(*pending, return_exceptions=True)` gives it those turns and returns when
every cancelled task is really finished. `return_exceptions=True` collects their
`CancelledError`s as values, so this line does not raise.

**Build the answer** from the original `tasks` list (input order). For a done task,
`task.exception()` returns the exception or `None`; it never raises for a task that finished
normally or with an error.

**The empty case.** `asyncio.wait([])` raises `ValueError: Set of Tasks/Futures is empty`, so
return `[]` first.

## Code

```python
import asyncio


async def gather_within(coro_fns, timeout):
    if not coro_fns:
        return []
    tasks = [asyncio.create_task(fn()) for fn in coro_fns]
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)

    results = []
    for task in tasks:
        if task not in done:
            results.append(None)
        elif task.exception() is not None:
            results.append(task.exception())
        else:
            results.append(task.result())
    return results
```

## Complexity

n tasks, O(n) bookkeeping. Wall time is about `min(timeout, slowest call)` plus the longest
cleanup of a cancelled call.

## Another way

Wrap each call so it never raises, and put a deadline around a TaskGroup:

```python
results = [None] * len(coro_fns)

async def run(i, fn):
    try:
        results[i] = await fn()
    except Exception as error:          # CancelledError is not an Exception: it passes
        results[i] = error

try:
    async with asyncio.timeout(timeout):
        async with asyncio.TaskGroup() as group:
            for i, fn in enumerate(coro_fns):
                group.create_task(run(i, fn))
except TimeoutError:
    pass
return results
```

When the deadline fires the TaskGroup cancels the children **and waits for them**, so the
cleanup guarantee comes for free, and the empty list needs no special case. A slot written by a
call that finished in time keeps its value.

`asyncio.wait_for(asyncio.gather(...), timeout)` is *not* a solution: on timeout it cancels the
gather and you lose the results that had already finished.
