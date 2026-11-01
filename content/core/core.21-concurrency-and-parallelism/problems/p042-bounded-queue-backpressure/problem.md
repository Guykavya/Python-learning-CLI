# Backpressure with a bounded queue

A log shipper reads lines from a huge file (or a never-ending stream) and uploads each one. If
reading is faster than uploading, an **unbounded** queue just grows until the machine runs out
of memory. The fix is **backpressure**: a bounded queue (`asyncio.Queue(maxsize=...)`) makes
`await queue.put(...)` *wait* while the queue is full, so the producer can never get more than
`maxsize` items ahead of the consumers.

Write `async def produce_consume(items, consume, maxsize, n_consumers) -> list`:

- `items` is any iterable, possibly a **generator** that reads lazily. Take items from it
  **one at a time** as there is room. Never turn it into a list first.
- `consume` is an `async` function: `result = await consume(item)`.
- Use one `asyncio.Queue(maxsize=maxsize)`, one producer, and `n_consumers` consumer tasks that
  run `consume` concurrently.
- Return the list of results in the **same order as the items**.
- When the function returns, every consumer task must have **finished** (not just be stuck
  waiting on an empty queue). Use one sentinel per consumer, or `queue.join()` and then cancel
  the consumers (and wait for them).

You may assume `consume` does not raise.

**Example**

```python
def read_lines():
    for i in range(10):
        print("read", i)
        yield f"line {i}"

async def upload(line):
    await asyncio.sleep(0.02)
    return line.upper()

await produce_consume(read_lines(), upload, maxsize=2, n_consumers=3)
# ['LINE 0', 'LINE 1', ..., 'LINE 9']
# and "read 9" is printed only after most uploads have started: the reader is held back
```
