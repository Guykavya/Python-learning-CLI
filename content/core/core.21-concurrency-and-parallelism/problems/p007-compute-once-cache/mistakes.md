- One lock around the whole `get`, including `compute()`. Correct counts, but every key waits
  for every other key: the parallel test fails.
- Locking only the store (`with lock: values[key] = value`). The check still happens outside,
  so all threads compute.
- Forgetting the second check after getting the key lock. The waiting threads compute again
  one after another, so the count is 8 instead of 1 (just slower).
- Creating the per-key lock without the guard lock (`if key not in locks: locks[key] = Lock()`).
  Two threads can create two different locks for the same key, and both compute.
- Holding the guard lock while calling `compute()`. That is the "one big lock" again, hidden.
- Caching the exception, or leaving a lock held when `compute` raises. Use `with`, so the lock is
  released, and only store on success.
