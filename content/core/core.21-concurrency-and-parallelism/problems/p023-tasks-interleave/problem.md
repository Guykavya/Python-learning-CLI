# Trace: tasks take turns

How the event loop picks what runs next (enough to trace this program exactly):

- The loop keeps a **ready queue** (first in, first out) of tasks that can run.
- `asyncio.create_task(coro)` puts the new task at the **end** of the ready queue. It does
  **not** run it yet: the task starts only when the current code reaches an `await` that
  pauses.
- `await asyncio.sleep(0)` pauses the current task and puts it back at the **end** of the
  ready queue, so every task already waiting gets one turn first.
- `await some_task` on a task that is not finished pauses until that task finishes. When a
  task finishes, whoever is waiting for it goes to the **end** of the ready queue.
- A task runs without interruption from one pause to the next.

What does this program print?

```python
import asyncio


async def worker(name, steps):
    for i in range(steps):
        print(f"{name} step {i}")
        await asyncio.sleep(0)
    print(f"{name} done")
    return name


async def main():
    t1 = asyncio.create_task(worker("A", 2))
    t2 = asyncio.create_task(worker("B", 3))
    print("tasks created")
    await asyncio.sleep(0)
    print("main after sleep(0)")
    r1 = await t1
    print("main got", r1)
    r2 = await t2
    print("main got", r2)
    t3 = asyncio.create_task(worker("C", 1))
    print("C done?", t3.done())
    await asyncio.sleep(0.01)
    print("C done?", t3.done())


asyncio.run(main())
```

**Example**: the first line is `tasks created`. `create_task` only queues A and B; `main`
keeps running until its first `await`.

Write in `answer.txt` the lines the program prints, in order.
