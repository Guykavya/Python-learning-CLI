## Hint 1

Split the work: `start` only **creates** tasks (`asyncio.create_task`) and keeps them in a list;
`_worker` is the loop with a `try/finally` for the log; `stop` does the shutdown. In `stop`,
what is the difference between *asking* a task to stop and *knowing* it has stopped? Which
call waits for many tasks without raising when some of them were cancelled or crashed?

## Hint 2

For "stop twice is safe", make `stop` take the list **away** from the service before doing
anything, so a second call finds it empty. For the returned errors: `gather(...,
return_exceptions=True)` gives one outcome per task: `None`, a `CancelledError` (a
`BaseException`) or a real crash (an `Exception`).

```
start(n):
    if tasks: raise RuntimeError
    tasks = [create_task(self._worker(i)) for i in range(n or workers)]

_worker(i):
    log "start i"
    try: loop forever: await job(i)
    finally: log "stop i"

stop():
    tasks, self._tasks = self._tasks, []
    for t in tasks: t.cancel()
    outcomes = await gather(*tasks, return_exceptions=True)
    return [o for o in outcomes if isinstance(o, Exception)]
```
