# Producer-consumer pipeline with a Queue

One thread per item does not scale: 10,000 items would mean 10,000 threads. The classic
design is a **fixed set of worker threads** that take jobs from a `queue.Queue`. The queue is
already thread-safe, so the workers need no lock to share it.

Write `pipeline(items, work, n_workers)`:

- Start exactly `n_workers` worker threads.
- The main thread (the **producer**) puts every item on a queue, together with its index.
- Each worker (a **consumer**) loops: take a job from the queue, compute `work(item)`, store
  the result at its index.
- Workers must know when to stop. After the real jobs, put one **sentinel** (a special value
  such as `None`) on the queue **per worker**. A worker that takes a sentinel leaves its loop.
- `join` every worker before returning, so no thread is left running.
- Return the results **in input order**.

You may assume `work` does not raise.

**Example**

```python
import time, threading

def slow_upper(word):
    time.sleep(0.1)
    return (word.upper(), threading.current_thread().name)

out = pipeline(["red", "green", "blue", "pink", "gray", "teal"], slow_upper, 3)
print([w for w, _ in out])
print(len({name for _, name in out}), "different threads")
```

```text
['RED', 'GREEN', 'BLUE', 'PINK', 'GRAY', 'TEAL']
3 different threads
```

Six jobs of 0.1 s with three workers take about 0.2 s. (Which worker got which word changes
from run to run; the result order does not.)
