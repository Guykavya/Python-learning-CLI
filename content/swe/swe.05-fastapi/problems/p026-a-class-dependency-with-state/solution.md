## Approach

```python
class RateLimit:
    def __init__(self, limit: int, window: float):
        self.limit = limit
        self.window = window
        self.hits = {}                      # api key -> list of request times, oldest first

    def __call__(self, x_api_key: Annotated[str, Header()], now: Annotated[float, Depends(get_clock)]) -> str:
        recent = [t for t in self.hits.get(x_api_key, []) if now - t < self.window]
        if len(recent) >= self.limit:
            retry = max(1, math.ceil(recent[0] + self.window - now))
            self.hits[x_api_key] = recent
            raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": str(retry)})
        recent.append(now)
        self.hits[x_api_key] = recent
        return x_api_key


def create_app() -> FastAPI:
    app = FastAPI()
    search_limit = RateLimit(3, 60)         # one object per endpoint: it keeps its own counts
    export_limit = RateLimit(1, 10)

    @app.get("/search")
    def search(key: Annotated[str, Depends(search_limit)]):
        return {"key": key, "results": []}
    ...
```

Three ideas meet here:

1. **A callable instance is a dependency.** FastAPI inspects `search_limit.__call__`: it sees a header parameter and a sub-dependency (`get_clock`), resolves both, and calls the object. `__init__`'s arguments (`3, 60`) are *configuration*, chosen once when you write `RateLimit(3, 60)`; `__call__`'s arguments are *per request*.
2. **State on `self`.** The object lives as long as the app, so `self.hits` survives between requests. Making the objects inside `create_app` gives each app (and each test) fresh counts.
3. **An injected clock.** `now` comes from `get_clock`, so the test moves time by changing a number instead of sleeping for a minute.

Trace of the example: hits `[0, 10, 20]`; at t=25 all three still count (25, 15, 5 seconds old), so 429; the first to expire is t=0, at t=60, so `Retry-After: 35`. At t=60, `60 - 0 < 60` is false, so `recent = [10, 20]`, there is room, and `60` is added.

Storing `recent` back (also on the 429 path) throws away expired times, so the lists do not grow forever for a busy key.

## Complexity

O(limit) time per request (the list never holds more than `limit` times after cleaning) and O(keys × limit) memory.

## Another way

A **fixed window** counter: `key -> (window_start, count)`, reset when `now >= window_start + window`. It needs O(1) memory per key, but allows bursts at the edge (3 requests at t=59 and 3 more at t=60). A real deployment with several server processes keeps the counts in Redis instead of `self`, because each process would otherwise have its own limiter.
