## Approach

**Backpressure.** `asyncio.Queue(maxsize=2)` holds at most 2 items. `await queue.put(x)` on a
full queue suspends the producer until a consumer `get`s something. Because the producer pulls
the next item from `items` only after the previous `put` finished, the generator is read at the
speed of the consumers, never faster. At any moment the producer is at most `maxsize` items
(in the queue) plus one (in its hand) ahead.

That only works if `items` is iterated **lazily**. `list(items)` or `[x for x in items]` reads
the whole source first, which for a 50 GB log is the very memory problem we are avoiding.

**Order.** Each item travels with its index. Consumers write `results[index]`; at the end the
dict is turned back into a list in index order. (`results` is a dict, not a list, because we
do not know the length of a generator in advance.)

**Clean shutdown.** A consumer blocked on `await queue.get()` waits forever unless told to stop.
After the last real item the producer puts one sentinel per consumer. Each consumer takes
exactly one sentinel (it returns right after), so every consumer stops. The sentinels also go
through the bounded queue, so they wait their turn behind real items. `_DONE = object()` is a
unique object that can never be confused with a real item (`None` could be a real item).

`asyncio.TaskGroup` waits for the producer and all consumers. If one crashed with a bug it
would cancel the others too, instead of leaving them blocked.

Trace with `maxsize=1`, one consumer, items `a, b, c`:

| Step | Producer | Queue | Consumer |
|---|---|---|---|
| 1 | pulls `a`, puts it | `[a]` | |
| 2 | pulls `b`, `put` waits (full) | `[a]` | gets `a`, consumes |
| 3 | `put b` completes, pulls `c`, waits | `[b]` | |
| 4 | | `[b]` | finishes `a`, gets `b` |
| 5 | `put c` completes; puts DONE (waits) | `[c]` | ... |

## Code

```python
import asyncio

_DONE = object()


async def produce_consume(items, consume, maxsize, n_consumers):
    queue = asyncio.Queue(maxsize=maxsize)
    results = {}

    async def producer():
        for index, item in enumerate(items):
            await queue.put((index, item))
        for _ in range(n_consumers):
            await queue.put(_DONE)

    async def consumer():
        while True:
            entry = await queue.get()
            if entry is _DONE:
                return
            index, item = entry
            results[index] = await consume(item)

    async with asyncio.TaskGroup() as group:
        group.create_task(producer())
        for _ in range(n_consumers):
            group.create_task(consumer())
    return [results[i] for i in range(len(results))]
```

## Complexity

O(n) puts and gets. The queue holds at most `maxsize` items, so the memory for items in transit
is O(maxsize + n_consumers) however long the input is. (The results list is O(n), because the
caller asked for all of them; a real shipper would not keep them.)

## Another way

Without sentinels: run the producer to the end, then `await queue.join()` (it returns when
every item that was put has been marked with `queue.task_done()`), then `cancel()` the consumer
tasks and `await asyncio.gather(*consumers, return_exceptions=True)` so they have really
finished. The consumers then must call `queue.task_done()` after each item, and they end by
cancellation instead of by returning. Python 3.13 also added `queue.shutdown()`, after which
`get()` on an empty queue raises `asyncio.QueueShutDown`, a built-in version of the sentinel.
