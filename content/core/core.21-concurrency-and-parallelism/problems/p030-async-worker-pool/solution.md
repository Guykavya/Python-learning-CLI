## Approach

The pieces and why each is there:

- **The queue holds `(index, item)` pairs.** Workers finish in any order; the index tells a
  worker where to write `results[index]`. Pre-filling `results = [None] * len(items)` makes
  "failed slot is `None`" automatic.
- **`n_workers` tasks, each a `while True` loop.** A worker handles one item at a time, so
  concurrency is exactly `n_workers` (when there are enough items).
- **`task_done()` in `finally`.** The queue counts unfinished items: `put` adds one,
  `task_done` removes one, and `join()` waits for zero. If a failing item skipped
  `task_done`, `join()` would wait forever.
- **`except Exception` inside the loop.** A failure is recorded and the worker moves on. If
  the exception escaped, that worker task would die and its share of the queue would be left
  for the others (or for nobody).
- **Cancel, then await the workers.** After `join()` returns, every worker is paused in
  `await queue.get()` on an empty queue and would wait forever. `cancel()` raises
  `CancelledError` there; `gather(..., return_exceptions=True)` waits until they have really
  ended (and collects the `CancelledError`s instead of raising them). The `try/finally` also
  cleans up if `process` itself is cancelled while waiting in `join()`.
- **Sort the errors.** They are appended in finishing order; the task wants index order.

## Code

```python
import asyncio


async def process(items, worker, n_workers):
    queue = asyncio.Queue()
    for index, item in enumerate(items):
        queue.put_nowait((index, item))
    results = [None] * len(items)
    errors = []

    async def run():
        while True:
            index, item = await queue.get()
            try:
                results[index] = await worker(item)
            except Exception as exc:
                errors.append((index, exc))
            finally:
                queue.task_done()

    tasks = [asyncio.create_task(run()) for _ in range(n_workers)]
    try:
        await queue.join()
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    errors.sort(key=lambda pair: pair[0])
    return results, errors
```

No lock is needed around `results` or `errors`: asyncio switches tasks only at `await`, and
`results[index] = ...` and `errors.append(...)` contain no `await`.

## Complexity

O(n) time for the bookkeeping plus about `ceil(n / n_workers)` job lengths of wall time;
O(n) memory for the queue and results. Only `n_workers` tasks exist, however large `n` is,
which is the advantage over "one task per item plus a semaphore" (p029).

## Another way

Instead of cancelling, send one **sentinel** (`None`) per worker after the real items; a
worker that gets the sentinel calls `task_done()` and returns. Python 3.13 added
`queue.shutdown()`: after it, `get()` on an empty queue raises `asyncio.QueueShutDown`, which
the worker can catch to exit its loop. Both avoid cancelling, at the cost of a little more
code in the worker.
