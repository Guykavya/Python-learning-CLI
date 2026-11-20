import json
import time


def get_single_flight(cache, key, loader, ttl=60, lock_ttl=10, poll=0.005, timeout=5.0):
    """Only one caller loads; the others wait for its result."""
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    lock_key = f"lock:{key}"
    if cache.set(lock_key, "1", ex=lock_ttl, nx=True):      # I won the right to load
        try:
            value = loader(key)
            cache.set(key, json.dumps(value), ex=ttl)
            return value
        finally:
            cache.delete(lock_key)
    deadline = time.monotonic() + timeout                   # somebody else is loading
    while time.monotonic() < deadline:
        cached = cache.get(key)
        if cached is not None:
            return json.loads(cached)
        time.sleep(poll)
    return loader(key)                                      # the loader died or is too slow
