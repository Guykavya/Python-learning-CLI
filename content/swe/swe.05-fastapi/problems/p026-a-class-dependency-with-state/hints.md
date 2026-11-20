## Hint 1

Where can the limiter keep its memory? Not in a local variable of `__call__` (it disappears after each request), but on `self`, because FastAPI calls the **same object** every time. What data structure maps each API key to its recent request times?

## Hint 2

On each call: build `recent` = the times of this key with `now - t < window`. If `len(recent) >= limit`, the oldest one (`recent[0]`, since you append in time order) is the first to expire, at `recent[0] + window`. Otherwise append `now`. In `create_app`, make one `RateLimit(...)` per endpoint and use it as `key: Annotated[str, Depends(limiter)]`.

## Hint 3

```text
__init__: self.limit, self.window, self.hits = {}      # key -> [times]

__call__(x_api_key, now):
    recent = [t for t in self.hits.get(x_api_key, []) if now - t < self.window]
    if len(recent) >= self.limit:
        retry = max(1, ceil(recent[0] + self.window - now))
        raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": str(retry)})
    recent.append(now); self.hits[x_api_key] = recent
    return x_api_key

create_app: search_limit = RateLimit(3, 60); export_limit = RateLimit(1, 10)
            search(key: Annotated[str, Depends(search_limit)]) ...
```
