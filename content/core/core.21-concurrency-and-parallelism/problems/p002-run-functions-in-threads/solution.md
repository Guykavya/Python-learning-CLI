## Approach

1. Make a list `results` with one slot per call.
2. Define an inner function `call(index, args)` that runs `func(*args)` and stores the value at
   `results[index]`. Each thread writes to a **different** slot, so no lock is needed: there is
   no read-modify-write on shared data.
3. Create one `Thread` per tuple, **start them all**, then **join them all**.

Starting and joining in separate loops is the whole point. `t.start(); t.join()` inside one
loop waits for each thread before the next starts, which is just a slow sequential loop.

Storing by index is what keeps input order: the threads finish in any order, but each value
lands in its own slot.

## Code

```python
import threading


def run_in_threads(func, args_list):
    results = [None] * len(args_list)

    def call(index, args):
        results[index] = func(*args)

    threads = [
        threading.Thread(target=call, args=(i, args))
        for i, args in enumerate(args_list)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
```

## Complexity

n threads, each running one call. Wall time is about the time of the **slowest** call (plus a
little start-up per thread) when the calls are waiting (I/O, `sleep`). For CPU-bound Python
code the GIL makes the total about the same as running them one by one. Memory: one thread
stack per call, so this is only for small n. For many items use a pool (p017).

## Another way

`concurrent.futures.ThreadPoolExecutor().map(lambda args: func(*args), args_list)` does the
same thing with a fixed number of reusable threads and keeps input order for you. Writing it
by hand once shows what the pool does inside.
