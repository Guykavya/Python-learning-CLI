# Single flight with a lock

Chapter section 6.1 (the stampede). When a hot key is missing and 20 requests arrive at once, a naive cache sends 20 loads to the database. **Single flight** lets exactly one caller load. The lock is a Redis key set with `SET lock:<key> 1 NX EX <lock_ttl>`: only one caller can create it. The others poll the cache until the value appears.

## What to write

```python
def get_single_flight(cache, key, loader, ttl=60, lock_ttl=10, poll=0.005, timeout=5.0): ...
```

1. If `cache.get(key)` has a value, return `json.loads` of it.
2. Otherwise try to take the lock `lock:<key>` with `cache.set(f"lock:{key}", "1", ex=lock_ttl, nx=True)`.
3. **If you got it:** call `loader(key)`, store `json.dumps(value)` under `key` with `ex=ttl`, return the value. **Always** delete the lock afterwards, also when the loader raises (use `try`/`finally`). An exception from the loader goes to the caller.
4. **If you did not get it:** somebody else is loading. Every `poll` seconds look in the cache again; return the value as soon as it is there. If `timeout` seconds pass without a value (the loader died, or is too slow), call `loader(key)` yourself and return its result, so no caller hangs for ever.

Use `time.monotonic()` and `time.sleep()` for the waiting loop (real time: the tests use threads).

## Example

```python
cache, loader = MiniRedis(), Loader(delay=0.05)        # each load takes 50 ms
results = run_concurrently(lambda: get_single_flight(cache, "hot", loader), n=20)
loader.calls                     # 1
len(results)                     # 20, every result == {'key': 'hot', 'value': 42}
cache.get("lock:hot")            # None: the lock was released
```

The tests start 20 threads at the same instant with a `threading.Barrier` and check invariants only (exactly one load, every caller answered), so they do not depend on luck.
