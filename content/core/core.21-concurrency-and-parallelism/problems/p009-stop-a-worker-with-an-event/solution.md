## Approach

A thread cannot be stopped from outside, so the worker must check a flag. With a plain
`time.sleep(interval)` it only checks between sleeps, so a stop request can wait up to a whole
interval (or an hour, for an hourly job).

`Event.wait(timeout)` is a sleep that can be cut short. It blocks until the event is set **or**
the timeout passes, and returns `True` in the first case and `False` in the second. Using it as
the pause in the loop makes the worker:

- tick once per interval while nobody asks it to stop;
- return immediately when `stop.set()` is called, wherever it is in the wait.

## Code

```python
def worker(stop, tick, interval):
    count = 0
    while not stop.is_set():
        tick()
        count += 1
        if stop.wait(interval):
            break
    return count
```

The `while not stop.is_set()` handles "already stopped" (returns 0 without ticking). The
`break` is not strictly needed, because the `while` condition would also see the set event,
but it makes the intent clear.

## Complexity

O(number of ticks). While waiting, the thread uses no CPU: `Event.wait` blocks on a lock
inside, it does not poll.

## Another way

`threading.Timer(interval, fn)` runs `fn` once after a delay in a new thread and can be
`cancel()`ed, but for a repeating job a loop with `Event.wait` is simpler and needs only one
thread. In asyncio code (later in this module) the same idea is a task cancelled with
`task.cancel()` while it waits in `await asyncio.sleep(interval)`.
