import json
import time


def get_single_flight(cache, key, loader, ttl=60, lock_ttl=10, poll=0.005, timeout=5.0):
    # This is the NAIVE version: every concurrent miss loads. Turn it into single flight.
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    value = loader(key)
    cache.set(key, json.dumps(value), ex=ttl)
    return value
