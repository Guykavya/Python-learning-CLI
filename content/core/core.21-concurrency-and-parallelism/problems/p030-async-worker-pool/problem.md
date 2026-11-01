# A worker pool with `asyncio.Queue`

The classic shape for bounded async work: put all jobs in a queue, start `n` **worker
tasks** that each loop "take a job, do it, take the next", wait until the queue is fully
processed, then stop the workers.

Write `async def process(items, worker, n_workers)` in `solution.py`:

- `worker(item)` is an `async def` function that returns a result or raises.
- Exactly `n_workers` worker tasks process the items, so at most `n_workers` calls to
  `worker` run at once (and with enough items, exactly that many).
- Use an `asyncio.Queue`, `queue.task_done()` and `await queue.join()` to know when all
  items are processed.
- A failing item must not kill its worker: record it and keep going.
- When everything is processed, **cancel** the worker tasks (they are stuck in
  `await queue.get()` forever otherwise) and wait for them to finish, so no task is left
  running after `process` returns.
- Return `(results, errors)`:
  - `results` is a list as long as `items`, in input order; slot `i` holds the result for
    `items[i]`, or `None` if that item failed.
  - `errors` is a list of `(index, exception)` pairs, sorted by index.

**Example**

```python
import asyncio

async def worker(n):
    await asyncio.sleep(0.01 * n)
    if n == 3:
        raise ValueError("three is bad")
    return n * 10

results, errors = asyncio.run(process([5, 1, 3, 2], worker, 2))
print(results)   # [50, 10, None, 20]
print(errors)    # [(2, ValueError('three is bad'))]
```
