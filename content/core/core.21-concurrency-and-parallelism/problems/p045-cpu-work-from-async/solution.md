## Approach

The event loop is one thread. A plain function call inside a coroutine runs on that thread
until it returns; there is no `await` in it, so the loop cannot switch to another task. With
the starter, 8 jobs of 0.1 s freeze the loop for 0.8 s and the heartbeat stops.

`loop.run_in_executor(executor, func, *args)` submits `func(*args)` to the executor and returns
an `asyncio.Future` **at once**. The work happens on a pool thread; the loop thread is free
until the future completes. Starting all of them before awaiting lets `workers` jobs run at the
same time, and `asyncio.gather` collects the results in argument order and re-raises the first
error.

`asyncio.get_running_loop()` is the way to get the loop from inside a coroutine (the old
`get_event_loop()` is discouraged).

Threads help here because `time.sleep` (like file and network I/O, and many C libraries)
releases the GIL. For pure-Python CPU work, threads would still take turns on the GIL; pass a
`ProcessPoolExecutor` and the same `handle_jobs` code runs the work on several cores. The
function must then be importable (top level of a module) and its arguments and result must be
picklable, and the program needs the `if __name__ == "__main__":` guard.

## Code

```python
import asyncio


async def handle_jobs(jobs, cpu_fn, executor):
    loop = asyncio.get_running_loop()
    futures = [loop.run_in_executor(executor, cpu_fn, job) for job in jobs]
    return await asyncio.gather(*futures)
```

## Complexity

n jobs on w workers: about `ceil(n / w)` job durations of wall time. The loop thread itself does
only O(n) bookkeeping.

## Another way

`await asyncio.to_thread(cpu_fn, job)` is shorter, but it always uses the loop's **default**
thread pool. You cannot choose processes, and you share the pool (and its size limit) with
everything else in the program that uses `to_thread`. Passing an executor explicitly lets the
caller decide: a small thread pool for a sync database driver, a process pool for image work.

`run_in_executor` passes only positional arguments. For keyword arguments use
`functools.partial(cpu_fn, job, quality=80)`.
