## Approach

`asyncio.gather` starts one task per URL so they can all wait at the same time. The
`asyncio.Semaphore(limit)` is a counter of free slots: `async with semaphore` takes a slot (or
waits until one is free) and gives it back when the block ends, even on an error. Every task
reaches the semaphore immediately, but only `limit` get past it; the others queue up and enter
as earlier requests finish.

The semaphore must be **one object shared by all tasks**, created once in the function. And it
must wrap the `await client.get(...)`, because that is the part that is "in flight".

`gather` returns results in the order of its arguments, so `zip(urls, codes)` pairs them up
correctly even though requests finish in a different order.

## Code

```python
import asyncio

import httpx


async def fetch_many(client: httpx.AsyncClient, urls: list[str], limit: int) -> dict[str, int]:
    semaphore = asyncio.Semaphore(limit)

    async def status_of(url: str) -> int:
        async with semaphore:
            response = await client.get(url)
            return response.status_code

    codes = await asyncio.gather(*(status_of(url) for url in urls))
    return dict(zip(urls, codes))
```

## Complexity

n requests. Wall time is about `ceil(n / limit)` request times when they all take the same
time. Memory O(n) for the tasks and the result, although only `limit` responses are being
received at once.

## Another way

A worker pool: put the URLs in an `asyncio.Queue` and start exactly `limit` worker tasks that
loop `url = await queue.get()` until the queue is empty. This creates `limit` tasks instead of
n, which matters for millions of URLs. httpx can also cap connections itself with
`httpx.AsyncClient(limits=httpx.Limits(max_connections=limit))`, but that limit belongs to the
client (shared by every caller) and does not apply to the fake transport in the tests; the
semaphore expresses the rule in your own code.
