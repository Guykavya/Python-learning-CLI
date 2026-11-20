## Approach

```python
@app.get("/report/{n}")
async def report(n: int):
    return await asyncio.to_thread(make_report, n)      # waits in a worker thread; the loop stays free
```

What happens with three requests at once:

1. Request 1 reaches `await asyncio.to_thread(...)`. `make_report(10)` starts in a worker thread, and the coroutine pauses, giving control back to the loop.
2. The loop starts request 2: another worker thread. Then request 3: a third.
3. Three threads sleep at the same time. After about 0.3 s each finishes, the loop resumes each coroutine, and the three responses go out.

Before the change, step 1 ran `make_report` on the loop itself, so steps 2 and 3 waited 0.3 s each.

Pass the function and its arguments **separately**: `to_thread(make_report, n)`. Writing `to_thread(make_report(n))` calls the function first, on the loop, and only then hands its *result* to the thread.

## Complexity

The work is the same; the wall time for k concurrent requests drops from about 0.3·k s to about 0.3 s (up to the size of the thread pool).

## Another way

`await run_in_threadpool(make_report, n)` from `fastapi.concurrency` does the same with Starlette's thread pool, the one plain `def` endpoints use. Or, if nothing in the endpoint needs `await`, make it a plain `def` and let FastAPI move the whole endpoint to a thread. For heavy **CPU** work in pure Python, threads do not help (the GIL); use a process pool or a task queue (section 10.3's note).
