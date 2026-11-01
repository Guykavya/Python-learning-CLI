## Hint 1

Inside `async with asyncio.TaskGroup() as tg:`, `tg.create_task(coro)` starts a task that
belongs to the group. The `async with` block does not end until every task in the group has
finished. What happens when one of them raises? Where do the results live once the block is
over?

## Hint 2

Keep the task objects in a list (in `loaders` order). After the `async with` block, all of
them are done, so `task.result()` is safe. If any failed, the block raises an
`ExceptionGroup` and the line after it never runs, which is what we want.

```
async with TaskGroup() as tg:
    tasks = [tg.create_task(loader()) for loader in loaders]
return [t.result() for t in tasks]
```
