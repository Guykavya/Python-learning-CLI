# A report that survives failures

A dashboard loads data for many user ids at once. Some ids fail (missing user, server
error). One bad id must not throw away all the good answers.

Write `async def fetch_report(ids, fetch)` in `solution.py`:

- `fetch(id)` is an `async def` function that returns data or raises an exception.
- Run all fetches **concurrently**.
- Return a tuple `(ok, failed)` of two dicts:
  - `ok` maps each id whose fetch succeeded to its result (even if the result is `0`,
    `None` or an empty list: that is still a success).
  - `failed` maps each id whose fetch raised to the **name of the exception type**, for
    example `"KeyError"`.
- Every fetch runs to its end: a fast failure must not stop the slower ones.
- Both dicts keep the order of `ids`.

Use `asyncio.gather(..., return_exceptions=True)`.

**Example**

```python
import asyncio

async def fetch(user_id):
    await asyncio.sleep(0.01 * user_id)
    if user_id == 2:
        raise KeyError(user_id)
    if user_id == 4:
        raise TimeoutError("server too slow")
    return f"user-{user_id}"

print(asyncio.run(fetch_report([1, 2, 3, 4], fetch)))
# ({1: 'user-1', 3: 'user-3'}, {2: 'KeyError', 4: 'TimeoutError'})
```
