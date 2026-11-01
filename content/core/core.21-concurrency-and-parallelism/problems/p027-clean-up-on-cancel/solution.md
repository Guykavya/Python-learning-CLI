## Approach

Look at what the starter does wrong:

| Case | Starter | Result |
|---|---|---|
| success | releases after the work | fine |
| `work` raises | the `release` line is skipped | leak |
| cancelled in `work` | `except CancelledError: return None` | leak, **and** the cancel is swallowed |

Cancellation in asyncio is just an exception (`CancelledError`, a `BaseException`) thrown in
at the `await` where the task is paused. So the tool for "always clean up" is the same as
for any exception: `try/finally`. A `finally` block runs on `return`, on any exception, and on
`CancelledError`, and afterwards the exception keeps propagating by itself.

Swallowing the cancel is a real bug, not just bad style: whoever cancelled the task
(a `TaskGroup`, `asyncio.timeout`, a server shutting down) waits for the task to end **as
cancelled**. If it returns `None` instead, a timeout cannot become `TimeoutError` and a
shutdown thinks the work finished.

Where the `try` starts matters too. If the cancel hits during `acquire()`, `conn` does not
exist yet. With `acquire()` **before** the `try`, the `finally` does not run in that case,
so nothing is released.

## Code

```python
async def use_resource(pool, work):
    conn = await pool.acquire()
    try:
        return await work(conn)
    finally:
        pool.release(conn)
```

## Complexity

O(1) extra time and memory per call. The fix costs nothing; the leak costs the whole pool.

## Another way

If you must react to the cancel (log it, roll back a transaction), catch it, do the work,
and **re-raise** with a bare `raise`:

```python
    except asyncio.CancelledError:
        log("request cancelled, rolling back")
        raise
    finally:
        pool.release(conn)
```

Real pools offer an async context manager, `async with pool.connection() as conn:`, whose
`__aexit__` releases the connection; writing one is p034. `contextlib.asynccontextmanager`
around this same `try/finally` gives you that.
