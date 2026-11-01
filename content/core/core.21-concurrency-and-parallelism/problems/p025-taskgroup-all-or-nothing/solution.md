## Approach

A `TaskGroup` is a "nursery" for tasks: every task created with `tg.create_task` belongs to
the group, and the `async with` block does not end until **all** of them have ended. That
gives two guarantees `gather` does not:

1. **No task outlives the block.** If one task fails, the group cancels every other task,
   waits until they have really finished (their `except CancelledError` and `finally` blocks
   ran), and only then raises.
2. **No error is lost.** The block raises an `ExceptionGroup` that holds every exception that
   happened (not just the first). The caller handles it with `except*`.

So the function is tiny: create the tasks in the group, keep them in a list in `loaders`
order, and after the block read `task.result()` from each. If anything failed, the line
after the block never runs.

## Code

```python
import asyncio


async def load_all(loaders):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(loader()) for loader in loaders]
    return [task.result() for task in tasks]
```

## Complexity

Wall time is the slowest loader if all succeed, or the time of the first failure plus the
time the others need to finish cancelling. O(n) memory for the tasks.

## Another way

`gather` can be made to cancel the others by hand:

```python
tasks = [asyncio.create_task(l()) for l in loaders]
try:
    return list(await asyncio.gather(*tasks))
except BaseException:
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)   # wait for them to stop
    raise
```

That is what `TaskGroup` does for you, plus collecting every error. Use `gather(...,
return_exceptions=True)` when failures are independent (a report, p024) and `TaskGroup` when
the results only make sense together.
