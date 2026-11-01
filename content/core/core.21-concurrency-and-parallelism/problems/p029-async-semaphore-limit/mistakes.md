- Creating the semaphore but calling `fn()` outside `async with sem:`. The permit is taken
  and returned without guarding anything.
- `await sem.acquire()` without a matching `sem.release()` in a `finally`. One failing job
  loses a permit forever; after `limit` failures everything hangs.
- Creating `asyncio.Semaphore(limit)` at module level. It is shared by every call, so two
  calls with different limits interfere (and before Python 3.10 it was tied to one loop).
- Fixed batches of `limit` with `gather` per batch. Correct limit, but slower.
- Forgetting the `limit < 1` check. `Semaphore(0)` makes every job wait forever.
