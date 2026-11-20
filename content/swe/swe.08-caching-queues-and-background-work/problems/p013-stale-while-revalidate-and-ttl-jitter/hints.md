## Hint 1

There are two clocks in each entry: Redis's own expiry (the hard deadline, after which `get` returns `None`) and the `soft_expires` time written **inside** the JSON. Which one tells you "serve it, but someone should refresh"?

## Hint 2

```text
raw = cache.get(key)
if raw is None: value = loader(key); store(value); return value, "cold miss"
entry = json.loads(raw)
if entry["soft_expires"] > now(): return entry["value"], "fresh"
if not cache.set("lock:"+key, "1", ex=10, nx=True): return entry["value"], "stale"
try:
    value = loader(key)
except Exception: return entry["value"], "stale"
else: store(value); return value, "refreshed"
finally: cache.delete("lock:"+key)

store(value): cache.set(key, json.dumps({"value": value, "soft_expires": now() + jittered(soft, rng)}),
                        ex=jittered(hard, rng))
```
