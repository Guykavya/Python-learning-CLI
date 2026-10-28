## Approach

All five decorators share one skeleton: a factory that checks its settings, a `decorator` that
creates the per-function state, and a `wrapper` that does the work on each call. What changes is
only what the wrapper does around `func(*args, **kwargs)`:

| Decorator | Before the call | After the call | On an exception |
|---|---|---|---|
| `timer` | read the clock | append the elapsed time (in `finally`) | still append, re-raise |
| `retry` | | return the result | sleep and try again, or re-raise |
| `cache` | look up the key; on a fresh hit return early | store the result | store nothing |
| `rate_limit` | drop old times; raise if full; record the time | | |
| `logger` | append `call` | append `return` | append `raise`, re-raise |

**Dependency injection.** `clock` and `sleep` are parameters. Real code uses the defaults;
tests pass a fake clock that only moves when the test says so. This is why none of the tests
needs to wait, and why the results are exact numbers instead of "about 3 seconds".

**LRU with a plain dict.** Since Python 3.7 a dict keeps insertion order. Popping a key and
inserting it again moves it to the end, so the dict's order is "least recently used first".
The first key is the one to evict.

**State per function.** The cache dict, the counters and the list of call times are created in
`decorator`, so two functions decorated by the same `cache()` or `rate_limit(...)` result do
not share them.

## Code

```python
import time
from functools import wraps


def timer(log, clock=time.perf_counter):
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
```

## Complexity

- `timer`, `logger`: O(1) extra per call.
- `retry`: up to `attempts` calls and `attempts - 1` sleeps.
- `cache`: O(1) average per call plus building the key (sorting k keyword items: O(k log k)).
  Memory: up to `maxsize` entries.
- `rate_limit`: O(calls) per call to filter the list, which never holds more than `calls` times.

## Another way

- `functools.lru_cache(maxsize=...)` gives you the LRU part ready-made (in C, so faster), but it
  has no `ttl`. A common trick is to add a "time bucket" argument: `get(item, int(clock() // 60))`
  makes the key change every minute.
- `collections.deque` with `popleft()` is the classic structure for the rate limiter's window:
  removing old times from the left is O(1) each instead of rebuilding the list.
- For the rate limiter, the **token bucket** algorithm is another popular choice: a bucket
  refills at a steady rate and each call takes one token. It allows short bursts while keeping
  the same average rate.
- Python's `logging` module is what real programs use instead of a list; the list here makes the
  behaviour easy to test.
