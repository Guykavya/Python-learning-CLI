## Approach

A semaphore is a counter of permits. `async with sem:` waits until the counter is above 0,
takes one permit, runs the block, and gives the permit back when the block ends (also when
the block raises or is cancelled). With `limit` permits, at most `limit` jobs can be inside
their blocks at any moment.

So:

1. Check `limit`. `Semaphore(0)` is legal but nothing could ever take a permit, so every job
   would wait forever. A clear `ValueError` is better than a silent hang.
2. Wrap each job: `async with sem: return await fn()`.
3. `gather` all the wrappers. They all **start** at once, but only `limit` get past the
   `async with`; the others wait in line. When one finishes, the next waiter goes in
   immediately: no fixed batches, so a slow job never holds up a whole batch.

`gather` returns results in argument order, so the order rule needs no extra code.

## Code

```python
import asyncio


async def run_limited(coro_fns, limit):
    if limit < 1:
        raise ValueError(f"limit must be at least 1, got {limit}")
    sem = asyncio.Semaphore(limit)

    async def one(fn):
        async with sem:
            return await fn()

    return list(await asyncio.gather(*(one(fn) for fn in coro_fns)))
```

## Complexity

Wall time is about `ceil(n / limit)` job lengths for equal jobs. Memory is O(n): all `n`
wrapper tasks exist at once, but only `limit` do real work. For a truly huge `n`
(millions), a worker pool with a queue (p030) keeps only `limit` tasks alive instead.

## Another way

Split the jobs into batches of `limit` and `gather` one batch at a time. It respects the
limit but is slower: each batch waits for its slowest job while the free slots sit idle.

A worker pool (p030) is the other common shape: `limit` worker tasks pull jobs from an
`asyncio.Queue`.
