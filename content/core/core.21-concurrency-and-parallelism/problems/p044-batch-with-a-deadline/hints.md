## Hint 1

You need three steps: wait **at most** `timeout`, stop the late ones, and make sure they have
*really* stopped. Which asyncio function waits for a set of tasks with a timeout and tells you
which are done and which are still pending, **without** cancelling anything itself? After
`task.cancel()`, has the task finished, or only been asked to?

## Hint 2

```
if not coro_fns: return []
tasks = [create_task(fn()) for fn in coro_fns]
done, pending = await asyncio.wait(tasks, timeout=timeout)
for t in pending: t.cancel()
await asyncio.gather(*pending, return_exceptions=True)   # cleanup runs here

for t in tasks (input order):
    not in done        -> None
    t.exception()      -> that exception
    else               -> t.result()
```
