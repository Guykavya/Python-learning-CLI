## Approach

The queue connects one producer and many consumers. `Queue.put` and `Queue.get` take care of
all the locking, and `get()` blocks while the queue is empty, so idle workers sleep instead of
spinning.

- **Order:** each job is `(index, item)`; the worker writes `results[index]`. Different
  workers write different slots, so no lock is needed.
- **Stopping:** a queue has no "closed" state, so we send a **sentinel**. Each worker stops
  after taking **one** sentinel, so we put exactly `n_workers` of them, after all real jobs
  (FIFO order means every real job is taken before any sentinel).
- **Clean finish:** `join()` each worker, so when `pipeline` returns, all work is done and no
  thread is left.

Real jobs are tuples, so even an item equal to `None` arrives as `(1, None)`, never as the bare
sentinel. Testing with `is` (not `==` or truthiness) keeps `0` and `""` safe too.

## Code

```python
import queue
import threading

_STOP = None


def pipeline(items, work, n_workers):
    jobs = queue.Queue()
    results = [None] * len(items)

    def consumer():
        while True:
            job = jobs.get()
            if job is _STOP:
                break
            index, item = job
            results[index] = work(item)

    workers = [threading.Thread(target=consumer) for _ in range(n_workers)]
    for w in workers:
        w.start()
    for job in enumerate(items):
        jobs.put(job)
    for _ in workers:
        jobs.put(_STOP)
    for w in workers:
        w.join()
    return results
```

## Complexity

O(n) queue operations; wall time about `ceil(n / n_workers)` rounds of `work` when `work`
waits on I/O. Only `n_workers` threads exist, however many items there are.

## Another way

- Use `queue.task_done()` after each job and `jobs.join()` in the producer to wait until every
  job is processed, then stop the workers (with sentinels, or make them daemon threads). That
  is useful when the workers live on after this batch.
- `queue.Queue(maxsize=...)` makes `put` block when the queue is full, which keeps a fast
  producer from filling memory (backpressure, p042).
- `ThreadPoolExecutor(n_workers).map(work, items)` is this whole function in one line; it uses
  a queue and worker threads inside.
