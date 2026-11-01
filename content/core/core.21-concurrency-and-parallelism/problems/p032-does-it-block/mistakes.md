- "It is inside `async def`, so it does not block." The keyword changes nothing about
  `time.sleep` or `requests.get`.
- Putting `await` in front of a sync call: `await requests.get(url)`. The call still blocks,
  then `await` fails with `TypeError` because a `Response` is not awaitable.
- Fixing CPU work with `to_thread`. The loop stays responsive, but the work does not get
  faster, and other threads compete for the GIL; a process pool is the real fix.
- Calling every line "blocking" (including `await asyncio.sleep`), or calling every short
  line "fine" (including `sum(range(10**8))`, which takes about a second).
- Sharing one `sqlite3` connection across `to_thread` calls. By default a connection may only
  be used in the thread that created it.
