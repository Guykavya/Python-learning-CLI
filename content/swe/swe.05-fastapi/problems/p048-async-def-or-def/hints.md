## Hint 1

For each body, find the slow line (network, database, disk), if there is one. Then ask: is there an `await` in front of it? If the slow line is **not** awaited, what does the event loop do while it waits? Remember the three lines of section 10.2: `/async-good`, `/async-bad`, `/sync-ok`.

## Hint 2

- A library is "async" only if you call it with `await` (`httpx.AsyncClient`, `AsyncSession`, `asyncio.sleep`). `requests`, a normal SQLAlchemy `Session`, `open()` and `Path.read_text()` all **block**.
- Blocking call → `def` (FastAPI moves it to a worker thread).
- Awaited call → `async def`.
- Nothing slow → either; `async def` saves a thread hand-off.

## Hint 3

```text
1 area         nothing slow           -> either (async def fine)
2 requests.get blocking network       -> def      (async def would freeze the loop)
3 await client awaited network        -> async def (required for await)
4 sync Session blocking database      -> def      (or AsyncSession + await)
5 read_text    blocking disk          -> def
blocking call inside async def        -> await run_in_threadpool(f, ...) / asyncio.to_thread(f, ...)
```
