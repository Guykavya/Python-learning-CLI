- `items = list(items)` "to know the length". It reads the whole source into memory before any
  backpressure can happen, and never ends on an infinite stream.
- `asyncio.Queue()` without `maxsize`, or `put_nowait`. The queue is unbounded (or raises
  `QueueFull`), so the producer is never held back.
- One sentinel for several consumers. The first consumer takes it and stops; the others wait
  on `get()` forever and the call never returns.
- Using `None` as the sentinel when `None` might be a real item.
- Appending results as they finish. Consumers finish out of order; keep the index.
- `queue.join()` and returning without stopping the consumers. They stay blocked on `get()`
  as orphan tasks (the test lists them).
- Cancelling the consumers but not awaiting them. They have not actually finished yet when you
  return.
- Calling `consume(item)` without `await`. You store coroutine objects, nothing is uploaded, and
  Python warns "coroutine was never awaited".
