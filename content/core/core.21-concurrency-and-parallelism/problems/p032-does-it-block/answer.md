1. **`time.sleep(2)`: blocks for 2 seconds.** It sleeps the whole thread, and the loop lives
   in that thread, so no other request is served. Fix: `await asyncio.sleep(2)` (if you just
   want to wait), or `await asyncio.to_thread(time.sleep, 2)` if it stands for some blocking
   call you cannot change.
2. **`requests.get(...)`: blocks** for the whole network round trip (often 100 ms to
   seconds). `requests` is a synchronous library: it waits on the socket without ever giving
   control back to the loop. Fix: an async client, `response = await client.get(url)` with
   `httpx.AsyncClient`, or `await asyncio.to_thread(requests.get, url)` as a stop-gap.
3. **`await asyncio.sleep(2)`: does not block.** The task pauses and the loop runs other
   tasks for those 2 seconds. Nothing to fix.
4. **The 50-million-step loop: blocks** for several seconds of pure CPU work. There is no
   `await`, so the loop never gets control. A thread would not help much (the GIL lets only
   one thread run Python code at a time). Fix: move it to a process:
   `await loop.run_in_executor(process_pool, heavy_function, 50_000_000)`, with the work in
   a top-level function.
5. **Reading a 2 KB local file: technically blocks, for microseconds.** Fine to leave as it
   is. It becomes a problem only for big files or slow disks (network drives); then use
   `await asyncio.to_thread(path.read_text)`.
6. **`await client.get(...)` with `httpx.AsyncClient`: does not block.** While waiting for
   the network, the task is paused at the `await` and the loop serves others. This is the
   correct way.
7. **`sum(range(10**8))`: blocks** for about a second or more of CPU work, even though it is one
   line. "One line" says nothing about time. Fix as for 4: a process pool via
   `run_in_executor`.
8. **The `sqlite3` query: blocks** for as long as the query takes. `sqlite3` is a
   synchronous driver; fast queries on a small database are a few milliseconds, slow ones
   much more, and the loop is frozen meanwhile. Fix: `await asyncio.to_thread(run_query,
   uid)` (a small function that opens its own connection, since a sqlite3 connection should
   be used from one thread), or an async driver such as `aiosqlite`.

**The rule behind all eight:** inside `async def`, only an `await` on something that really
pauses lets other tasks run. Waiting with a sync library blocks: give it a thread
(`to_thread`) or use an async library. Long computing blocks: give it a process.
