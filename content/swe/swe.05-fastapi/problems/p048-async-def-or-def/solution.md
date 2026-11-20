## Approach

Find the slow line, then ask whether it is awaited. See `answer.md` for the full model answer and checklist.

| # | Slow part | Blocks or awaited? | Choice |
|---|---|---|---|
| 1 | none | - | either (`async def` saves a thread hand-off) |
| 2 | `requests.get` | blocks | `def` |
| 3 | `await client.get` | awaited | `async def` |
| 4 | sync `session.get` | blocks | `def` |
| 5 | `read_text` | blocks | `def` |

Example of the wrong choice: endpoint 2 as `async def`. Ten users ask for the weather at once and the weather service takes 2 s. The first call blocks the event loop for 2 s; the second starts only after that; the tenth user waits 20 s. Meanwhile even `/area`, which needs microseconds, waits behind them. As a plain `def`, the ten calls wait in ten worker threads at the same time and everybody gets an answer after about 2 s.

## Complexity

Not applicable. (The cost model: an awaited wait costs almost nothing; a blocking wait costs one thread for its duration, and the pool has 40 threads by default; a blocking wait on the loop costs everyone.)

## Another way

When in doubt, choose `def`: a `def` endpoint that does no blocking work only pays a small thread hand-off, while an `async def` endpoint that blocks hurts the whole server. Measure with the method of section 10.2: fire several requests at once with `httpx.AsyncClient` and `asyncio.gather` and compare the total time with one request's time.
