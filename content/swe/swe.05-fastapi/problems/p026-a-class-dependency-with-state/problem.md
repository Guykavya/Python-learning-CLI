# A class dependency with state

Chapter sections 3.4 (headers), 9.3 and 9.4 (class dependencies), 9.6 (an injected clock). `__call__` is from core.10 (special methods).

Section 9.4 used a **class** as a dependency: FastAPI called the class and read its `__init__` parameters. Here you use an **instance** of a class instead. An object with a `__call__` method is callable, so `Depends(RateLimit(3, 60))` works: FastAPI reads the parameters of `__call__` and calls the object on every request. Because the *same object* is used for every request, it can **remember** things between requests. That is how you build a rate limiter.

Write `class RateLimit`:

- `RateLimit(limit, window)`: at most `limit` requests per API key in any `window` seconds.
- `__call__(self, x_api_key: Annotated[str, Header()], now: Annotated[float, Depends(get_clock)])`:
  - the API key comes from the header `X-API-Key` (required: a missing header is a 422);
  - the time comes from the dependency `get_clock` (already written: `time.monotonic()`), so a test can replace the clock;
  - a past request **still counts** while `now - t < window`; older ones are forgotten;
  - if the key already has `limit` requests that still count: raise `HTTPException(429, "Rate limit exceeded", headers={"Retry-After": "<seconds>"})`, where seconds = `math.ceil(oldest + window - now)`, at least 1. A **rejected** request is not recorded;
  - otherwise record `now` for this key and return the key.

Then write `create_app()` that makes a new app with its own limiters (so each test starts clean):

| Endpoint | Limiter | Answer |
|---|---|---|
| `GET /search` | `RateLimit(3, 60)` | `{"key": key, "results": []}` |
| `GET /export` | `RateLimit(1, 10)` | `{"key": key, "file": "export.csv"}` |

Each endpoint has its **own** instance, so the two counts are separate.

## Example

With a fake clock and the key `k1` on `/search`:

```text
t=0   -> 200        t=10 -> 200        t=20 -> 200
t=25  -> 429  Retry-After: 35     (the oldest, t=0, stops counting at t=60; 0 + 60 - 25 = 35)
t=25  -> 429  Retry-After: 35     (rejected requests are not recorded)
t=25, key k2 -> 200               (each key has its own count)
t=60  -> 200        (t=0 no longer counts: 60 - 0 < 60 is false; now counting 10, 20, 60)
t=61  -> 429  Retry-After: 9      (oldest is now 10: 10 + 60 - 61 = 9)
```

The tests import `create_app`, `RateLimit` and `get_clock`, and replace the clock with `app.dependency_overrides[get_clock] = lambda: clock.now`.
