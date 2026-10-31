"""A decorator toolkit: timer, retry, cache, rate_limit and logger.

Every decorator takes its slow or changing tools (clock, sleep) as arguments,
so tests can pass fake ones and never wait for real time.
"""

import time
from functools import wraps


def timer(log, clock=time.perf_counter):
    """Append (name, seconds) to log after every call, even when the call raises."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                log.append((func.__name__, clock() - start))
        return wrapper
    return decorator


def retry(attempts=3, exceptions=(Exception,), delay=0.1, backoff=2.0, sleep=time.sleep):
    """Call again after a matching exception, waiting delay, delay*backoff, ... in between."""
    if attempts < 1:
        raise ValueError(f"attempts must be at least 1, got {attempts}")
    if delay < 0:
        raise ValueError(f"delay must not be negative, got {delay}")
    if backoff < 1:
        raise ValueError(f"backoff must be at least 1, got {backoff}")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts:
                        raise
                    sleep(wait)
                    wait = wait * backoff
        return wrapper
    return decorator


def cache(maxsize=None, ttl=None, clock=time.monotonic):
    """Remember results. maxsize: keep at most this many (least recently used goes first).
    ttl: an entry is fresh while clock() - stored_at < ttl."""
    if maxsize is not None and maxsize < 1:
        raise ValueError(f"maxsize must be None or at least 1, got {maxsize}")
    if ttl is not None and ttl <= 0:
        raise ValueError(f"ttl must be None or positive, got {ttl}")

    def decorator(func):
        store = {}                      # key -> (value, stored_at), oldest use first
        stats = {"hits": 0, "misses": 0}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in store:
                value, stored_at = store.pop(key)
                if ttl is None or clock() - stored_at < ttl:
                    store[key] = (value, stored_at)     # re-insert: now the most recent
                    stats["hits"] += 1
                    return value
            stats["misses"] += 1
            value = func(*args, **kwargs)
            store[key] = (value, clock())
            if maxsize is not None and len(store) > maxsize:
                oldest = next(iter(store))
                del store[oldest]
            return value

        def cache_info():
            return {"hits": stats["hits"], "misses": stats["misses"], "size": len(store)}

        def cache_clear():
            store.clear()
            stats["hits"] = 0
            stats["misses"] = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper
    return decorator


def rate_limit(calls, period, clock=time.monotonic):
    """Allow at most `calls` calls in any window of `period` seconds.
    A call at time t stops counting at time t + period. Too many calls raise RuntimeError."""
    if calls < 1:
        raise ValueError(f"calls must be at least 1, got {calls}")
    if period <= 0:
        raise ValueError(f"period must be positive, got {period}")

    def decorator(func):
        recent = []                     # times of allowed calls, oldest first

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = clock()
            recent[:] = [t for t in recent if now - t < period]
            if len(recent) >= calls:
                wait = recent[0] + period - now
                raise RuntimeError(
                    f"rate limit exceeded for {func.__name__}: at most {calls} calls "
                    f"per {period}s, try again in {wait:.2f}s"
                )
            recent.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def logger(log):
    """Record ("call", name, args, kwargs), then ("return", name, result)
    or ("raise", name, exception class name)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log.append(("call", func.__name__, args, kwargs))
            try:
                result = func(*args, **kwargs)
            except Exception as err:
                log.append(("raise", func.__name__, type(err).__name__))
                raise
            log.append(("return", func.__name__, result))
            return result
        return wrapper
    return decorator
