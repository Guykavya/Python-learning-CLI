## Approach

**Start.** `asyncio.create_task` schedules a coroutine and returns immediately; the task runs
when the caller next awaits. `start` therefore does not need to be `async`, but it needs a
running loop. We keep the tasks in `self._tasks`. That list also protects them: the event loop
keeps only *weak* references to tasks, so a task nobody references can be garbage-collected
in the middle of its work.

**The worker.** `try: while True: await self.job(i)` / `finally: log "stop i"`. The `finally`
runs exactly once, whether the loop ends by cancellation (the `CancelledError` arrives at the
`await` inside `job`) or because `job` raised.

**Stop, in three steps.**

1. `tasks, self._tasks = self._tasks, []`: take ownership of the list. A second `stop()` (or
   one before `start()`) gathers an empty list and returns `[]` at once.
2. `task.cancel()` on each. This only **requests** cancellation; on a task that already
   crashed it does nothing.
3. `await asyncio.gather(*tasks, return_exceptions=True)`: wait until every task has finished,
   including any cleanup that itself awaits (the test's job sleeps 0.02 s while cleaning up).
   `return_exceptions=True` means the cancellations and crashes come back as values instead of
   being raised. `CancelledError` is a `BaseException`, not an `Exception`, so
   `isinstance(o, Exception)` keeps only real crashes.

**`async with`.** `__aenter__` calls `start()` and returns `self` (so `as service` works);
`__aexit__` awaits `stop()` and returns `False`, so an exception from the body goes on after
the workers are stopped.

One subtle case: if a task is cancelled **before it ever started running** (start, then stop
with no `await` in between), its coroutine body never runs at all, so neither `start i` nor
`stop i` is logged. "Cleanup exactly once" holds for every worker that started.

## Code

```python
import asyncio


class Service:
    def __init__(self, job, workers=2):
        self.job = job
        self.workers = workers
        self.log = []
        self._tasks = []

    @property
    def running(self):
        return bool(self._tasks)

    def start(self, n=None):
        if self._tasks:
            raise RuntimeError("service is already running")
        count = self.workers if n is None else n
        self._tasks = [
            asyncio.create_task(self._worker(i), name=f"worker-{i}") for i in range(count)
        ]

    async def _worker(self, worker_id):
        self.log.append(f"start {worker_id}")
        try:
            while True:
                await self.job(worker_id)
        finally:
            self.log.append(f"stop {worker_id}")

    async def stop(self):
        tasks, self._tasks = self._tasks, []
        for task in tasks:
            task.cancel()
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)
        return [o for o in outcomes if isinstance(o, Exception)]

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()
        return False
```

## Complexity

O(n) to start and to stop n workers. Shutdown time is the longest cleanup of any worker,
because all cleanups run concurrently.

## Another way

Use a `TaskGroup` owned by the service: `__aenter__` enters it and creates the workers,
`__aexit__` cancels them and exits it. That is shorter, but a TaskGroup treats a crashed worker
as fatal (it cancels all the others and raises an `ExceptionGroup`), while this service keeps
the healthy workers running and *reports* the crash at shutdown. Which behaviour is right
depends on the program; a web server usually wants the second.

Real services also stop on Ctrl+C or `SIGTERM`. With `asyncio.run`, Ctrl+C cancels the main
task, so an `async with Service(...)` block in `main` shuts the workers down cleanly for free.
On Unix, `loop.add_signal_handler(signal.SIGTERM, ...)` can trigger the same path.
