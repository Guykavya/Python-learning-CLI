## Approach

`SET NX EX` is an atomic "create if absent": the winner loads, everybody else polls. `try`/`finally` releases the lock even when the loader fails, and the expiry on the lock is the safety net if the winner's whole process dies.

```python
import json
import time


def get_single_flight(cache, key, loader, ttl=60, lock_ttl=10, poll=0.005, timeout=5.0):
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    lock_key = f"lock:{key}"
    if cache.set(lock_key, "1", ex=lock_ttl, nx=True):
        try:
            value = loader(key)
            cache.set(key, json.dumps(value), ex=ttl)
            return value
        finally:
            cache.delete(lock_key)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        cached = cache.get(key)
        if cached is not None:
            return json.loads(cached)
        time.sleep(poll)
    return loader(key)
```

## Cost

One load per miss instead of one per concurrent caller. Waiters pay latency (up to the load time) and extra cache reads while polling: `load_time / poll` reads each. A failed load makes waiters spin until the timeout and then load themselves; a smarter version would store a short "error" marker so they give up sooner.

## Another way

**Stale-while-revalidate** (p013) avoids waiting entirely by serving the old value while one caller refreshes. **In-process coalescing** (`threading.Lock` per key, or `asyncio` futures) is cheaper but works per process only: N processes still send N loads. Note the lock released here with a plain `delete` could, in theory, delete a lock that expired and was taken by someone else; p016 fixes that with a token.
