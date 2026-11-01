# A service that shuts down gracefully

Long-running programs (a bot, a queue worker, a metrics sender) start background tasks that
loop forever. Starting them is easy. **Stopping** them well is the real work:

- every worker is told to stop (cancelled),
- shutdown **waits** until each worker has really finished, including its cleanup code,
- every cleanup runs **exactly once**,
- a worker that crashed earlier does not make shutdown crash; its error is reported,
- calling `stop()` twice (for example from a signal handler and from `finally`) is harmless.

Write `class Service`:

```python
service = Service(job, workers=2)
```

- `job` is an `async` function `job(worker_id)` that does one unit of work.
- `start(n=None)`: start `n` worker tasks (default: `workers`), with ids `0 .. n-1`. Must be
  called while the event loop is running. Calling it when already running raises
  `RuntimeError`.
- Each worker appends `f"start {i}"` to `service.log`, then calls `await job(i)` in a loop
  forever. When it ends, **for any reason** (cancelled, or `job` raised), it appends
  `f"stop {i}"`.
- `async def stop() -> list`: cancel all workers, **wait** for all of them to finish, and return
  the list of exceptions that workers died with (not counting the cancellations). After
  `stop()` the service is not running. Calling `stop()` again, or before `start()`, returns `[]`.
- `running` property: `True` between `start()` and `stop()`.
- `async with Service(job, workers=3) as service:` starts the workers on entry and stops them on
  exit, even if the body raises (the body's exception is not swallowed).

**Example**

```python
async def job(i):
    await asyncio.sleep(0.01)          # one unit of work

async with Service(job, workers=2) as service:
    await asyncio.sleep(0.05)
    service.running                     # True
service.running                         # False
sorted(service.log)                     # ['start 0', 'start 1', 'stop 0', 'stop 1']
```
