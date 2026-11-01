## Approach

Asyncio is **cooperative**: the loop can switch tasks only when the running task reaches an
`await` that pauses. `time.sleep(0.2)` is not an `await`; it holds the loop's only thread
for 0.2 s, and nothing else in the program can run. Five such calls freeze the program for a
full second, and they cannot overlap because the thread is busy.

`asyncio.to_thread(func, *args)` fixes both problems:

1. It sends `func(*args)` to a thread from the loop's default thread pool and returns an
   awaitable. Awaiting it pauses **only your task**; the loop's thread is free to run the
   heartbeat and other requests.
2. Because each lookup runs in its own thread, several can block at the same time. `gather`
   starts them all and returns results in input order.

`time.sleep` (and blocking I/O in general) releases the GIL, so the threads truly wait in
parallel.

## Code

```python
import asyncio


async def handle_all(requests, slow_lookup):
    return list(
        await asyncio.gather(*(asyncio.to_thread(slow_lookup, r) for r in requests))
    )
```

## Complexity

Wall time is about one lookup, as long as the number of requests is not more than the
default pool's size (`min(32, os.cpu_count() + 4)` threads); beyond that, extra lookups wait
for a free thread. Memory: one task per request plus the pool's threads.

## Another way

`loop.run_in_executor(executor, func, arg)` is the older, more general form of `to_thread`:

```python
loop = asyncio.get_running_loop()
futures = [loop.run_in_executor(None, slow_lookup, r) for r in requests]
return list(await asyncio.gather(*futures))
```

Passing your own `ThreadPoolExecutor(max_workers=...)` lets you choose the number of
threads, and passing a `ProcessPoolExecutor` is the way to run **CPU-heavy** work from async
code (threads would not help there because of the GIL). Best of all is an async library
(an async database driver, `httpx.AsyncClient`), which needs no threads at all.
