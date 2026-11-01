# Whatever finishes in time

A search page asks five backends for results and shows **whatever has arrived after 0.3
seconds**. Late backends are not an error; their slot is just empty. But they must not keep
running after the page is built: each one holds a connection that its `finally` block closes.

Write `async def gather_within(coro_fns, timeout) -> list`:

- `coro_fns` is a list of zero-argument **async functions**. Call each one and run them all
  concurrently as tasks.
- After `timeout` seconds (or sooner, if all are done), return a list in **input order**:
  - the return value for each call that finished successfully in time,
  - the **exception object** for each call that failed in time (returned, not raised),
  - `None` for each call that was not finished.
- Calls that were not finished must be **cancelled**, and you must **wait until their
  cancellation is complete** (their `finally` blocks, which may themselves `await`, have run)
  before you return.
- An empty list returns `[]`.

**Example**

```python
async def fast():  await asyncio.sleep(0.01); return "fast"
async def broken(): raise KeyError("x")
async def slow():
    try:
        await asyncio.sleep(10)
        return "slow"
    finally:
        await asyncio.sleep(0.01)         # close the connection
        log.append("slow cleaned up")

await gather_within([fast, broken, slow], timeout=0.1)
# ['fast', KeyError('x'), None]           after about 0.1 s
log
# ['slow cleaned up']                      already there when gather_within returns
```
