# Stale-while-revalidate and TTL jitter

Chapter section 6.2 (more defences) and 6.3 (cache avalanche). Single flight (p012) makes callers **wait** for the one loader. **Stale-while-revalidate** does better for data where a little staleness is fine: each entry has a **soft** deadline ("time to refresh") and a later **hard** deadline (Redis deletes it). Between the two, one caller refreshes and everyone else gets the old value **at once**. **Jitter** spreads deadlines so that thousands of keys loaded at the same second do not all expire at the same second (an avalanche).

## What to write

```python
def jittered(seconds, rng) -> float: ...
def get_swr(cache, key, loader, now, soft=60, hard=600, rng=random.random) -> tuple: ...
```

- `jittered(seconds, rng)` returns `seconds * (0.9 + 0.2 * rng())`: anywhere from 90% to 110%. `rng()` returns a float in [0, 1).
- Each cache entry is the JSON text `{"value": ..., "soft_expires": <time>}`, stored with `ex=jittered(hard, rng)`. Its `soft_expires` is `now() + jittered(soft, rng)`.
- `get_swr` returns `(value, status)`:

| Situation | What to do | Status |
|---|---|---|
| no entry in the cache | load, store a new entry | `"cold miss"` |
| entry and `soft_expires > now()` | return the cached value | `"fresh"` |
| past the soft deadline, and `cache.set(f"lock:{key}", "1", ex=10, nx=True)` succeeds | load, store a new entry, delete the lock | `"refreshed"` |
| past the soft deadline, the lock is taken | return the cached (stale) value **without waiting** | `"stale"` |
| you hold the lock but `loader` raises | delete the lock, return the old value | `"stale"` |

A cold miss that fails raises the loader's exception (there is nothing to serve).

## Example

```python
clock = FakeClock(0)
r = MiniRedis(now=clock)
mid = lambda: 0.5                                  # jittered(x, mid) == x
get_swr(r, "k", loader, clock, rng=mid)            # (42, 'cold miss')
clock.advance(30);  get_swr(r, "k", loader, clock, rng=mid)   # (42, 'fresh')
clock.advance(40)                                  # t = 70, past soft (60)
r.set("lock:k", "1", ex=10)                        # someone else is refreshing
get_swr(r, "k", loader, clock, rng=mid)            # (42, 'stale')  -- loader not called
r.delete("lock:k")
get_swr(r, "k", loader, clock, rng=mid)            # (value, 'refreshed')
```

The tests give you `r` (MiniRedis on a fake clock) and `clock` (call it for the time).
