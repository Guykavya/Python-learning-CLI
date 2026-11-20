# Who blocks the event loop?

Chapter sections 10.1 (what the event loop does, the table of `async def` versus `def`) and 10.2 (seeing it). The event loop itself is from core.21.

The program below defines four endpoints. Each one "works" for 0.3 seconds in a different way and returns the **name of the thread** that ran it. Then, for each endpoint in turn, it sends **three requests at the same moment** (`asyncio.gather` over an in-process `httpx.AsyncClient`, as in section 10.2) and prints:

- `together` if all three finished in less than 0.6 s (they overlapped: about 0.3 s), otherwise `one-at-a-time` (about 0.9 s);
- `main` if all three ran on the event-loop thread (`MainThread`), otherwise `worker`.

The exact seconds differ between machines, but these two words do not.

```python
import asyncio
import threading
import time

import httpx
from fastapi import FastAPI

app = FastAPI()


def wait_a_bit():
    time.sleep(0.3)


@app.get("/one")
async def one():
    time.sleep(0.3)
    return {"thread": threading.current_thread().name}


@app.get("/two")
def two():
    time.sleep(0.3)
    return {"thread": threading.current_thread().name}


@app.get("/three")
async def three():
    await asyncio.sleep(0.3)
    return {"thread": threading.current_thread().name}


@app.get("/four")
async def four():
    wait_a_bit()
    return {"thread": threading.current_thread().name}


async def three_at_once(path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        responses = await asyncio.gather(client.get(path), client.get(path), client.get(path))
        elapsed = time.perf_counter() - start
    threads = {r.json()["thread"] for r in responses}
    return elapsed, threads


for path in ["/one", "/two", "/three", "/four"]:
    elapsed, threads = asyncio.run(three_at_once(path))
    verdict = "together" if elapsed < 0.6 else "one-at-a-time"
    where = "main" if threads == {"MainThread"} else "worker"
    print(f"{path} {verdict} {where}")
```

Write your answer in `answer.txt`: four lines, one per endpoint, in the format of the `print`: the path, the verdict, the thread, separated by single spaces (for example `/x together main`). Do not run it.

## After you answer

1. `/four` calls `wait_a_bit()`, a plain `def` function. Why does that not move the sleep to a worker thread?
2. `/two` and `/three` are both `together`. What is different about *how* they overlap, and which one would cope better with 1,000 requests at once?
3. How would you fix `/one` without turning it into a plain `def`? (Section 10.3.)
