## Approach

A semaphore holds a number of free places. `acquire()` takes one (or waits until one is free);
`release()` gives one back and wakes a waiting thread. With `limit` places, at most `limit`
threads can be between `acquire` and `release` at once, which is exactly the limit we want.

So:

1. Create **one** `BoundedSemaphore(limit)` for the whole call, before the threads start.
2. In each thread, wrap the call of `func` in `with places:`. The extra threads start, reach
   the `with`, and sleep there until a place is free.
3. Keep results by index, as in p002.

`with` matters: if `func` raises, the place must still be given back, or the remaining threads
wait forever.

`BoundedSemaphore` is the same as `Semaphore` but raises `ValueError` if someone releases more
times than they acquired, which turns a silent bug ("the limit slowly grows") into an error.

## Code

```python
import threading


def run_limited(funcs, limit):
    results = [None] * len(funcs)
    places = threading.BoundedSemaphore(limit)

    def call(index, func):
        with places:
            results[index] = func()

    threads = [threading.Thread(target=call, args=(i, f)) for i, f in enumerate(funcs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
```

## Complexity

n threads exist (most of them waiting), but at most `limit` do work at once. The wall time is
about `ceil(n / limit)` rounds of work. For large n this is wasteful: 10,000 waiting threads
still cost memory. A pool with `limit` workers (`ThreadPoolExecutor(max_workers=limit)`,
p017) gives the same limit with only `limit` threads.

## Another way

Acquire in the main thread before starting each thread, and release at the end of the thread.
Then at most `limit` threads even **exist** at once. It works, but acquire and release now
happen in different threads, which is easy to get wrong; a pool does this properly.
The asyncio version of this problem uses `asyncio.Semaphore` in the same way (p029).
