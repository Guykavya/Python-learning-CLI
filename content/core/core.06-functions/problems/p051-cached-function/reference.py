def make_cached(func):
    """Return (cached, stats): cached(*args) memoises func; stats() gives hits and misses."""
    cache = {}
    hits = 0
    misses = 0

    def cached(*args):
        nonlocal hits, misses
        if args in cache:
            hits += 1
        else:
            misses += 1
            cache[args] = func(*args)
        return cache[args]

    def stats():
        return {"hits": hits, "misses": misses}

    return cached, stats
