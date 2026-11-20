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
        return entry["value"], "stale"                    # someone else refreshes; do not wait
    try:
        value = loader(key)
    except Exception:
        return entry["value"], "stale"                    # keep serving the old value
    else:
        _store(cache, key, value, now, soft, hard, rng)
        return value, "refreshed"
    finally:
        cache.delete(lock_key)
