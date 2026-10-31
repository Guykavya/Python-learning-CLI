class CacheStats:
    # TODO: make this a TypedDict with the int keys hits, misses, evictions, size, capacity
    pass


# TODO: make LRUCache generic over K (keys) and V (values), and add the hints
class LRUCache:
    def __init__(self, capacity, on_evict=None):
        # TODO: validate capacity, keep a dict (insertion order = use order) and the counters
        pass

    def get(self, key):
        return None

    def put(self, key, value):
        pass

    def pop(self, key):
        raise KeyError(key)

    def peek(self, key):
        return None

    def keys(self):
        return []

    def items(self):
        return []

    def clear(self):
        pass

    def stats(self):
        return {}

    def __len__(self):
        return 0

    def __contains__(self, key):
        return False


def lru_memoize(capacity):
    # TODO: a decorator factory that caches results in an LRUCache
    def decorator(func):
        return func

    return decorator
