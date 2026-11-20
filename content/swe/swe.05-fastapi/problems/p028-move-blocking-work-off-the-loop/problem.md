# Move blocking work off the loop

Chapter sections 10.1, 10.2 and 10.3 (`run_in_threadpool` and `asyncio.to_thread`). `asyncio.to_thread` is from core.21.

The endpoint `GET /report/{n}` must stay an **`async def`** (imagine it also awaits an async database call). But it has to call `make_report(n)`, an old blocking function that takes 0.3 s (it stands for a slow library call; here it is `time.sleep(0.3)` plus a sum). The starter calls it directly:

```python
@app.get("/report/{n}")
async def report(n: int):
    return make_report(n)          # blocks the event loop for 0.3 s
```

So three users asking at once wait 0.3, 0.6 and 0.9 s: the loop is frozen while each report is made, exactly like `/one` in p027.

Change the endpoint so that `make_report` runs **in a worker thread** while the event loop keeps serving other requests. Use `await asyncio.to_thread(make_report, n)` (or `await run_in_threadpool(make_report, n)`; both are in section 10.3).

- The endpoint must still be `async def`.
- The result must not change: `{"n": n, "total": 0 + 1 + ... + (n - 1)}`.
- Call `make_report` through its name in `solution.py` (the test replaces it with a version that also records which thread ran it).

## Example

```text
GET /report/4   -> {"n": 4, "total": 6}
three GET /report/... at the same moment: all finish after about 0.3 s instead of 0.9 s
```

The test sends three requests at once with `httpx.AsyncClient(transport=httpx.ASGITransport(app=app))` and `asyncio.gather`, as in section 10.2, and requires them to finish in **less than 0.6 s** together. It also checks that `make_report` did not run on the main thread.
