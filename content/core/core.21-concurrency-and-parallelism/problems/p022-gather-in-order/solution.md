## Approach

Concurrency in asyncio needs the coroutines to exist **at the same time**, so the loop can
switch between them while each one waits. A `for` loop with `await` inside creates one
coroutine, waits for it to finish, and only then creates the next.

So first create all the coroutines (`fetch(name)` for every name: nothing runs yet), then
hand them all to `asyncio.gather`. `gather` turns each one into a task, the loop runs them
together, and when all are done `gather` returns their results **in the order of its
arguments**. You do not have to sort anything.

## Code

```python
import asyncio


async def fetch_all(names, fetch):
    return list(await asyncio.gather(*(fetch(name) for name in names)))
```

`gather()` with no arguments returns `[]`, so the empty case needs no special code. `gather`
already returns a list; `list(...)` just makes that promise explicit.

## Complexity

Wall time is the time of the **slowest** fetch, not the sum. Memory is O(n) for the tasks
and results. With thousands of names you would add a limit (an `asyncio.Semaphore`, see
p029) so you do not open thousands of connections at once.

## Another way

Create the tasks yourself and await them in order:

```python
tasks = [asyncio.create_task(fetch(name)) for name in names]
return [await t for t in tasks]
```

All tasks start before the first `await`, so they overlap; awaiting them in list order
keeps the input order. Or use `asyncio.TaskGroup` (see p025), which also cancels the others
if one fails.
