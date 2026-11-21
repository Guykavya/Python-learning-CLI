## Approach

```python
def recommendations(user, primary, cache, breaker, timeout=0.5, popular=POPULAR):
    try:
        items = breaker.call(lambda: primary(user, timeout=timeout))
    except Exception:
        if user in cache:
            return {"items": list(cache[user]), "stale": True, "source": "cache"}
        return {"items": list(popular), "stale": True, "source": "popular"}
    cache[user] = list(items)
    return {"items": list(items), "stale": False, "source": "primary"}
```

The three protections of chapter 12 work together: a **timeout** (the dependency may not hold you), a **circuit breaker** (a dependency that is down is not called at all: callers fail fast and the dependency can recover), and a **fallback decided in advance** (a stale answer is better than no page; a popular list is better than an empty box). The fallback is marked `stale=True`, so the page can show "showing earlier recommendations" instead of pretending. The chapter's table (12.4) gives the other cases: e-mail provider down -> queue it; payment provider timeout -> **do not guess**; search down -> a simple `LIKE` query labelled "limited results".

## Cost

A dictionary of last good answers per user (memory grows with users; in production a TTL cache such as Redis, swe.08) and a decision per dependency about what "degraded" means.

## Another way

Serve the stale value **first** and refresh in the background (stale-while-revalidate, swe.08 and swe.09), so a healthy dependency is not on the request path either. The circuit breaker's state should be exported as a metric (swe.09 section 10): an open circuit is something an operator wants to know about.
