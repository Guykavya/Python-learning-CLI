## Hint 1

Results must come out in input order, but the workers finish in any order. What can you put
in the queue **together with** each item so a worker knows where to store its result? And
how will `queue.join()` know that an item is finished, even when `worker` raised?

## Hint 2

Queue `(index, item)` pairs. Each worker loops forever; `task_done()` goes in a `finally` so
it is called for successes **and** failures. After `join()`, the workers are all waiting in
`get()`: cancel them and `gather` them so they really end.

```
queue = Queue(); for i, item in enumerate(items): queue.put_nowait((i, item))
results = [None] * len(items); errors = []
async def run():
    while True:
        i, item = await queue.get()
        try:    results[i] = await worker(item)
        except Exception as exc: errors.append((i, exc))
        finally: queue.task_done()
tasks = [create_task(run()) for _ in range(n_workers)]
await queue.join()
cancel every task; await gather(*tasks, return_exceptions=True)
return results, sorted(errors by index)
```
