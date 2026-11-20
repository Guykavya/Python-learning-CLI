## Hint 1

Only one caller can create a key with `nx=True`. So `cache.set("lock:hot", "1", ex=lock_ttl, nx=True)` is a race that exactly one caller wins. What should the winner do, and what should everybody else do? And why does the lock need `ex=`?

## Hint 2

```text
value in cache? -> return it
if set(lock, nx, ex):
    try:   value = loader(key); cache.set(key, json, ex=ttl); return value
    finally: cache.delete(lock)
deadline = monotonic() + timeout
while monotonic() < deadline:
    value in cache? -> return it
    sleep(poll)
return loader(key)               # fallback: never hang
```
