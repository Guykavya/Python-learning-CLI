# Trace: what cancellation really does

This is the module's tracing assessment. Cancellation is where most async bugs hide, and
the rules are precise:

1. `task.cancel()` does **not** stop the task on the spot. It only **requests** a cancel and
   returns `True` (or `False` if the task is already done). The task is woken up, and the
   next time it runs, a `CancelledError` is **raised inside it** at the `await` where it was
   paused.
2. Inside the task, `CancelledError` behaves like any exception: `except` blocks that match
   it run, `finally` blocks run.
3. If the task lets the `CancelledError` escape, the task ends as **cancelled**:
   `task.cancelled()` is `True`. If the task catches it and does not re-raise, the cancel was
   **swallowed**: the task goes on and ends normally with whatever it returns.
4. `gather(..., return_exceptions=True)` puts a `CancelledError` **object** in the result
   list for a cancelled task.
5. `async with asyncio.timeout(t):` cancels the current task when the time is up; when the
   `CancelledError` reaches the end of the block, it is turned into `TimeoutError`.
   `asyncio.wait_for(coro, t)` does the same for one awaitable.
6. New tasks wait in the ready queue (first in, first out) until the current code reaches an
   `await` that pauses; `await asyncio.sleep(0)` lets every waiting task run once.

What does this program print?

```python
import asyncio


async def polite(name):
    try:
        print(f"{name}: working")
        await asyncio.sleep(10)
        print(f"{name}: finished")
    except asyncio.CancelledError:
        print(f"{name}: cancelled, cleaning up")
        raise
    finally:
        print(f"{name}: finally")


async def stubborn(name):
    try:
        print(f"{name}: working")
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print(f"{name}: cancelled, but I swallow it")
    return f"{name} result"


async def slow():
    try:
        await asyncio.sleep(10)
    finally:
        print("slow: finally")


def show(r):
    return type(r).__name__ if isinstance(r, BaseException) else r


async def main():
    p = asyncio.create_task(polite("P"))
    s = asyncio.create_task(stubborn("S"))
    print("P done before it ran?", p.done())
    await asyncio.sleep(0)
    print("cancel P:", p.cancel())
    print("cancel S:", s.cancel())
    print("P done right after cancel?", p.done())
    results = await asyncio.gather(p, s, return_exceptions=True)
    print("results:", [show(r) for r in results])
    print("P cancelled?", p.cancelled(), "| S cancelled?", s.cancelled())
    print("cancel P again:", p.cancel())

    try:
        async with asyncio.timeout(0.05):
            await slow()
            print("after slow")
    except TimeoutError:
        print("main: TimeoutError from asyncio.timeout")

    try:
        await asyncio.wait_for(polite("W"), timeout=0.05)
    except TimeoutError as e:
        print("main: wait_for raised", type(e).__name__)

    print("main: end")


asyncio.run(main())
```

**Example**: the first line is `P done before it ran? False`. Creating the two tasks only
puts them in the ready queue; nothing has run yet, so `p` is not done.

Write in `answer.txt` the lines the program prints, in order. Then, for the assessment,
check yourself: can you say for **each** line **why** it appears exactly there?
