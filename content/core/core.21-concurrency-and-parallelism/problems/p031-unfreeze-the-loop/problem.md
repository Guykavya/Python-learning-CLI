# Unfreeze the event loop

An async web service looks up each request in an old library that has **no async version**:
`slow_lookup(request)` is a normal function that blocks (inside, it does `time.sleep`, like a
synchronous database driver or `requests.get`).

The current code calls it directly inside `async def`. While it runs, the whole event loop
is frozen: no other request is served, timers do not fire, even a "still alive" heartbeat
stops. And the lookups run one after another.

Write `async def handle_all(requests, slow_lookup)` in `solution.py`:

- Run `slow_lookup(r)` for every request **without blocking the event loop**: other tasks
  must keep running while the lookups happen.
- Run the lookups **concurrently**, so five 0.2-second lookups take about 0.2 s.
- Return the results in the order of `requests`.
- If a lookup raises, that exception itself propagates (a `LookupError` stays a `LookupError`,
  not wrapped in an `ExceptionGroup`). So `asyncio.gather` fits here better than `TaskGroup`.

Use `asyncio.to_thread`.

**Example**

```python
import asyncio
import time

def slow_lookup(r):
    time.sleep(0.2)          # blocking!
    return r.upper()

async def main():
    ticks = 0
    async def heartbeat():
        nonlocal ticks
        while True:
            await asyncio.sleep(0.02)
            ticks += 1
    hb = asyncio.create_task(heartbeat())
    result = await handle_all(["a", "b", "c", "d", "e"], slow_lookup)
    hb.cancel()
    print(result, "heartbeat ticks:", ticks)

asyncio.run(main())
```

With the blocking version: `['A', 'B', 'C', 'D', 'E'] heartbeat ticks: 0` after 1.0 s.
With your version: the same list, about **9 or 10** ticks (your number may differ a little), after
about 0.2 s.
