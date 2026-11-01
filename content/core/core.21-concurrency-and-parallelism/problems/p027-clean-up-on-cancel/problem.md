# Always give the connection back

A service borrows database connections from a small pool. Every borrowed connection must be
given back, whatever happens: success, an error, or the request being **cancelled** (the
user closed the page, a timeout fired, the server is shutting down). A connection that is
never returned is a **leak**; after a few leaks the pool is empty and the service hangs.

The pool has this interface:

- `await pool.acquire()` waits for a free connection and returns it. It may take a while.
- `pool.release(conn)` gives `conn` back. It is a normal (not async) method. Releasing a
  connection twice, or one you never got, is a bug and raises `RuntimeError`.

`starter.py` holds a version that leaks. Write `async def use_resource(pool, work)` in
`solution.py`:

1. Acquire a connection.
2. Return `await work(conn)`.
3. Release the connection **exactly once** in every case: success, `work` raising, or the
   task being cancelled while `work` runs.
4. If the task is cancelled while it is still waiting in `acquire()`, there is no connection
   yet, so nothing must be released.
5. Never swallow `asyncio.CancelledError`: after cleanup it must keep propagating, so the
   caller sees `task.cancelled() == True`. Other errors from `work` propagate too.

**Example**

```python
import asyncio

async def main():
    pool = Pool()   # some pool, e.g. the fake one in the tests

    async def slow_query(conn):
        await asyncio.sleep(10)
        return "rows"

    task = asyncio.create_task(use_resource(pool, slow_query))
    await asyncio.sleep(0.05)        # the task now holds a connection
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print(task.cancelled())          # True
    print(pool.in_use)               # 0   the connection came back
```
