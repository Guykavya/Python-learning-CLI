# All or nothing with `TaskGroup`

A page needs three pieces of data (user, orders, settings). If **any** of them fails, the
page cannot be built, so there is no point letting the other loaders keep working: they
should be **cancelled** right away, and the caller should see the error.

Write `async def load_all(loaders)` in `solution.py`:

- `loaders` is a list of `async def` functions that take no arguments.
- Run them all concurrently inside an `asyncio.TaskGroup`.
- If all succeed, return their results as a list **in the order of `loaders`**.
- If one fails, the `TaskGroup` cancels the others, waits for them to finish cancelling,
  and raises an `ExceptionGroup` holding the error(s). Let that `ExceptionGroup` propagate:
  do not catch it.

**Example**

```python
import asyncio

async def user():
    await asyncio.sleep(0.1)
    return "kavya"

async def orders():
    await asyncio.sleep(0.05)
    raise ConnectionError("orders service down")

async def settings():
    try:
        await asyncio.sleep(5)
        return {"theme": "dark"}
    except asyncio.CancelledError:
        print("settings: cancelled")
        raise

async def main():
    print(await load_all([user, user]))
    try:
        await load_all([user, orders, settings])
    except* ConnectionError as eg:
        print("caught:", eg.exceptions)

asyncio.run(main())
```

Output (after about 0.15 s in total, not 5 s):

```text
['kavya', 'kavya']
settings: cancelled
caught: (ConnectionError('orders service down'),)
```

When `orders` fails, the group cancels `user` and `settings` (only `settings` prints), waits for them to finish
cancelling, and only then raises the `ExceptionGroup`.
