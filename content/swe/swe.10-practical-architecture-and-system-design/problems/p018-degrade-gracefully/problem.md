# Degrade gracefully

Chapter sections 12.1 (timeouts), 12.3 (the circuit breaker) and 12.4 (fallbacks and graceful degradation), and the failure table of section 17. A page shows "recommended for you" from a separate recommendation service. When that service is slow or down, the page must **still load**: the dependency is not on the critical path. Decide **in advance** what the user sees, and never let the failure reach the page.

## What is given

The `CircuitBreaker` and `CircuitOpen` of chapter 12.3 are in the starter: `breaker.call(fn)` runs `fn()`; after `failure_threshold` failures in a row it is **open** and `call` raises `CircuitOpen` **without calling `fn`**; after `reset_after` seconds (by its injected `clock`) it lets one probe call through.

## What to write

```python
def recommendations(user, primary, cache, breaker, timeout=0.5, popular=("Python tips", "Testing basics", "Docker intro")) -> dict: ...
```

- `primary(user, timeout=...)` is the recommendation service: it returns a **list** of items, or raises any exception (a timeout, a connection error). Call it **through the breaker** and pass the `timeout` you were given: `breaker.call(lambda: primary(user, timeout=timeout))`.
- **Success:** remember the answer in `cache[user]` (a plain dict) and return `{"items": <the list>, "stale": False, "source": "primary"}`. An **empty list is a valid success** (the service answered "nothing for you").
- **Failure** (any `Exception` from the primary, **or** the open circuit): if `cache` has an entry for this user, return `{"items": <that list>, "stale": True, "source": "cache"}` (the last good answer, marked stale). If it has not, return `{"items": list(popular), "stale": True, "source": "popular"}` (a fixed popular list).
- **Never raise to the page.** (`KeyboardInterrupt` and other `BaseException`s are not "failures of the dependency": let them pass.)
- Return **new lists** (copies): a caller that changes the result must not damage the cache or the popular list.

## Example

```python
cache = {}
recommendations("ana", primary_ok, cache, breaker)     # {'items': ['a', 'b'], 'stale': False, 'source': 'primary'}
recommendations("ana", primary_down, cache, breaker)   # {'items': ['a', 'b'], 'stale': True,  'source': 'cache'}
recommendations("ben", primary_down, cache, breaker)   # {'items': ['Python tips', ...], 'stale': True, 'source': 'popular'}
```

After three failures the breaker opens; the next calls do not touch the primary at all (they fail fast and take the fallback), which protects both sides.
