## Approach

Keep the data past its "best before" time (soft) and let Redis delete it only at the hard deadline. One caller, chosen by `SET NX EX`, refreshes; everyone else is served the stale value immediately. A `try/except/else/finally` keeps the lock handling in one place.

```python
import json
import random


def jittered(seconds, rng):
    return seconds * (0.9 + 0.2 * rng())


def _store(cache, key, value, now, soft, hard, rng):
    entry = {"value": value, "soft_expires": now() + jittered(soft, rng)}
    cache.set(key, json.dumps(entry), ex=jittered(hard, rng))


def get_swr(cache, key, loader, now, soft=60, hard=600, rng=random.random):
    raw = cache.get(key)
    if raw is None:
        value = loader(key)
        _store(cache, key, value, now, soft, hard, rng)
        return value, "cold miss"
    entry = json.loads(raw)
    if entry["soft_expires"] > now():
        return entry["value"], "fresh"
    lock_key = f"lock:{key}"
    if not cache.set(lock_key, "1", ex=10, nx=True):
        return entry["value"], "stale"
    try:
        value = loader(key)
    except Exception:
        return entry["value"], "stale"
    else:
        _store(cache, key, value, now, soft, hard, rng)
        return value, "refreshed"
    finally:
        cache.delete(lock_key)
```

## Cost

Callers never wait for a load except on a cold miss. The price is staleness: between the soft deadline and the end of the refresh, users see data up to `soft + refresh time` old. Jitter costs nothing and turns one spike of expiries into a spread of ±10%.

## Another way

**Probabilistic early refresh** ("XFetch"): each request refreshes with a probability that rises as the deadline approaches, so a hot key is usually refreshed before it expires, with no lock at all. In a real web app the refresh itself can run in the background (a queued job or a thread) so even the "refreshed" caller does not wait.
