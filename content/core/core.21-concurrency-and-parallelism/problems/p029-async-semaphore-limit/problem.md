# At most N at a time with `asyncio.Semaphore`

`gather` starts **everything** at once. With 10,000 URLs that means 10,000 open connections:
the server blocks you, or your machine runs out of sockets. You want concurrency, but
**bounded**: at most `limit` jobs running at the same moment, and a new one starting as soon
as a slot frees up.

Write `async def run_limited(coro_fns, limit)` in `solution.py`:

- `coro_fns` is a list of `async def` functions that take no arguments.
- Run them concurrently, but never more than `limit` at the same time.
- Return their results in the **order of `coro_fns`**.
- If `limit` is less than 1, raise `ValueError` (a limit of 0 would wait forever).

Use `asyncio.Semaphore(limit)`.

**Example**

```python
import asyncio
import time

def job(n):
    async def run():
        await asyncio.sleep(0.1)
        return n * n
    return run

start = time.perf_counter()
print(asyncio.run(run_limited([job(n) for n in range(6)], 2)))
print(f"{time.perf_counter() - start:.1f} s")
```

Output (your time will differ slightly):

```text
[0, 1, 4, 9, 16, 25]
0.3 s
```

Six jobs of 0.1 s, two at a time: three "waves", about 0.3 s.
