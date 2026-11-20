## Model answer

**1. `area`: either works; `async def` is a fine choice.** Nothing in it is slow: one multiplication, no I/O. Running on the event loop for a few microseconds blocks nobody, and it avoids the small cost of handing the call to a worker thread. A plain `def` would also be correct, just slightly more overhead. (Only heavy CPU work, seconds of computation, is a problem in both: it belongs in a process pool or a job queue.)

**2. `weather` with `requests.get`: `def`.** `requests` is a **blocking** library: `requests.get` sits and waits for the network, and there is no `await` to give control back. In an `async def` it would freeze the **event loop** for up to 5 seconds, and *every* other request on that worker would wait too (the `/async-bad` line of section 10.2). As a plain `def`, FastAPI runs it in a **worker thread** from the **thread pool**: only that thread waits, the loop keeps serving others.

**3. `weather2` with `httpx.AsyncClient`: `async def` (it must be).** The slow part is **awaited**: while `await client.get(...)` waits for the network, the loop runs other requests. That is the best case: thousands of waits can overlap with no threads. It also *must* be `async def`, because `await` is a syntax error inside a plain `def`.

**4. `get_task` with a synchronous SQLAlchemy `Session`: `def`.** `session.get(...)` sends SQL through a normal database driver and **blocks** until the database answers. Inside `async def` that would stall the event loop on every query. As `def` it runs in the thread pool, which is exactly what sync drivers need. (To use `async def` you would switch to an `AsyncSession` and `await session.get(...)`, section 11.)

**5. `report` reading a file: `def`.** `path.read_text()` is ordinary **blocking** file I/O. For a small file on a fast disk it is quick, but on a slow or network disk it can take long, and in `async def` the whole loop would wait. `def` puts it on a worker thread at no risk.

**Calling blocking code from `async def`.** Push the blocking call to a thread and await it: `r = await run_in_threadpool(requests.get, url, timeout=5)` (from `fastapi.concurrency`) or `r = await asyncio.to_thread(requests.get, url, timeout=5)`. The loop stays free while the thread waits (section 10.3). Better still, replace `requests` with `httpx.AsyncClient`.

**Checklist: your answer should mention**
- [ ] `async def` runs on the **event loop**; `def` runs in a **worker thread** from the **thread pool**
- [ ] 1: nothing slow, so either works (async avoids the thread hand-off); heavy CPU work would be a problem in both
- [ ] 2: `requests` is **blocking**, so `def`; in `async def` it freezes every other request
- [ ] 3: the slow part is **awaited**, so `async def` (and `await` only works there)
- [ ] 4: a sync SQLAlchemy session blocks, so `def` (or switch to `AsyncSession` and await)
- [ ] 5: file reading blocks, so `def`
- [ ] the fix for blocking code inside `async def`: `run_in_threadpool` or `asyncio.to_thread`
