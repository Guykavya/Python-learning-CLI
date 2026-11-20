## Approach

Classify each endpoint by *where it runs* and *whether its waiting is an `await`*.

```text
/one one-at-a-time main
/two together worker
/three together main
/four one-at-a-time main
```

- **`/one`**: `async def`, so it runs on the event-loop thread (`main`). `time.sleep(0.3)` blocks that thread; the loop cannot start the second request until the first returns. Three requests take about 0.9 s: `one-at-a-time`. This is the chapter's "most common FastAPI performance bug".
- **`/two`**: plain `def`. FastAPI runs it in a worker thread from a pool, so the loop stays free and hands the next request to another thread. Three threads sleep at the same time: about 0.3 s, `together`, `worker`.
- **`/three`**: `async def` with `await asyncio.sleep(0.3)`. At each `await` the coroutine hands control back to the loop, which starts the next request. All three waits overlap on one thread: `together`, `main`.
- **`/four`**: the trap. FastAPI decides where to run by looking at the **endpoint** (`async def`), not at what it calls. `wait_a_bit()` is an ordinary function call, executed right there on the loop thread, so it blocks exactly like `/one`.

Real output of the program, run with FastAPI 0.162.0 and Pydantic 2.14.3 (five runs, identical every time).

## Complexity

Wall time for three concurrent requests: about 0.3 s when they overlap, about 3 × 0.3 s when they are serialised.

## Another way

Fix `/one` and `/four` inside `async def` by moving the blocking call off the loop: `await asyncio.to_thread(wait_a_bit)` or `await run_in_threadpool(wait_a_bit)` (section 10.3). Each call then waits in a worker thread while the loop serves others; the next problem, p028, does this.

The answer to "which copes with 1,000 requests": `/three`. Coroutines are cheap, while `def` endpoints share a limited thread pool (40 threads by default), so the 41st request waits for a free thread.
