# A caching client with ETags

Chapter section 11.5. Write a small client that avoids repeating work:

```python
class CachingClient:
    def __init__(self, client, clock): ...    # client: an httpx.Client; clock(): current time in seconds
    def get(self, url): ...                    # -> (body: bytes, source: str)
```

`source` tells where the body came from: `"network"` (a normal `200` response), `"cache"` (served without any request) or `"revalidated"` (a `304` confirmed the stored copy).

Rules:

1. A `200` response is **stored** when it has `Cache-Control: max-age=N` and/or an `ETag`. It is **fresh** for `N` seconds after it was received (`clock()` at that moment). `max-age` missing means "fresh for 0 seconds" (always revalidate).
2. A **fresh** stored response is returned from the cache with **no request**: `source == "cache"`.
3. A **stale** stored response with an `ETag` is revalidated: send the request with `If-None-Match: <etag>`. If the server answers `304 Not Modified`, return the stored body (`"revalidated"`) and make it fresh again for the `max-age` of the `304` response (none: fresh for 0 seconds). Any other answer is handled as a new response.
4. `Cache-Control: no-store` means the response must **never be stored**: delete any older copy of that URL. `no-cache` means "store, but revalidate every time" (fresh for 0 seconds).
5. Responses that are not `200` (`404`, `500`, ...) are returned as `"network"` and not stored, and they remove an older copy of that URL.
6. Each URL has its own entry.

The tests use `httpx.Client(transport=httpx.MockTransport(handler))` and a fake clock; the handler counts the requests.

## Example

```python
# server: 200, ETag: "v1", Cache-Control: max-age=60
c = CachingClient(client, clock)
c.get("http://x/a")     # (b"data", "network")           at t=0
c.get("http://x/a")     # (b"data", "cache")             at t=30: no request
c.get("http://x/a")     # (b"data", "revalidated")       at t=61: If-None-Match sent, server says 304
```
