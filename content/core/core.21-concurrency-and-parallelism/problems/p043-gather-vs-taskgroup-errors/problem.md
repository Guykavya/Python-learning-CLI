# Trace: one failure under gather and under TaskGroup

The same workload, three tasks where the middle one fails, is run three ways. What happens to
the **other** tasks, and what does the caller see?

- `await asyncio.gather(...)`: when one awaitable raises, `gather` raises **that** exception to
  the caller at once. The other tasks are **not** cancelled; they keep running in the
  background.
- `await asyncio.gather(..., return_exceptions=True)`: nothing is raised; exceptions are
  returned **in the result list** in their slot, and `gather` waits for all.
- `async with asyncio.TaskGroup()`: when one task fails, the group **cancels** the others,
  waits for them, then raises an `ExceptionGroup` holding the failure(s). `except*` matches
  exceptions inside a group.

Every sleep has a different length, so the order of events is fixed. `repr(ValueError('b'))`
is `ValueError('b')`, and printing a list shows the `repr` of each element.

What does this program print?

```python
import asyncio


async def job(name, delay, fail=False):
    try:
        await asyncio.sleep(delay)
        if fail:
            raise ValueError(name)
        print(f"{name} done")
        return name
    except asyncio.CancelledError:
        print(f"{name} cancelled")
        raise


async def with_gather():
    print("-- gather")
    try:
        await asyncio.gather(job("a", 0.01), job("b", 0.02, fail=True), job("c", 0.03))
    except ValueError as e:
        print("caught", repr(e))
    await asyncio.sleep(0.05)          # meanwhile, is c still running?
    print("gather over")


async def with_return_exceptions():
    print("-- return_exceptions")
    results = await asyncio.gather(
        job("d", 0.01), job("e", 0.02, fail=True), job("f", 0.03),
        return_exceptions=True,
    )
    print(results)


async def with_taskgroup():
    print("-- taskgroup")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(job("g", 0.01))
            tg.create_task(job("h", 0.02, fail=True))
            tg.create_task(job("i", 0.03))
        print("after the block")
    except* ValueError as group:
        print("caught", type(group).__name__, [str(e) for e in group.exceptions])
    print("taskgroup over")


async def main():
    await with_gather()
    await with_return_exceptions()
    await with_taskgroup()


asyncio.run(main())
```

**Example**: the first two lines are `-- gather` and `a done` (job `a` sleeps only 0.01 s and
succeeds before anything fails).

Write in `answer.txt` the lines the program prints, in order.
