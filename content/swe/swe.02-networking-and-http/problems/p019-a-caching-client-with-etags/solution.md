## Approach

```python
from dataclasses import dataclass


@dataclass
class _Entry:
    body: bytes
    etag: str
    fresh_until: float


def _directives(response):
    out = {}
    for part in response.headers.get("cache-control", "").split(","):
        name, _, value = part.strip().lower().partition("=")
        if name:
            out[name] = value
    return out


def _max_age(directives):
    value = directives.get("max-age")
    if value is not None and value.isdigit():
        return int(value)
    return None


class CachingClient:
    def __init__(self, client, clock):
        self.client = client
        self.clock = clock
        self.cache = {}

    def get(self, url):
        now = self.clock()
        entry = self.cache.get(url)
        if entry is not None and now < entry.fresh_until:
            return entry.body, "cache"
        headers = {}
        if entry is not None and entry.etag:
            headers["If-None-Match"] = entry.etag
        response = self.client.get(url, headers=headers)
        directives = _directives(response)
        if response.status_code == 304 and entry is not None:
            max_age = _max_age(directives)
            entry.fresh_until = now + max_age if max_age is not None else now
            return entry.body, "revalidated"
        if response.status_code == 200 and "no-store" not in directives:
            max_age = _max_age(directives)
            etag = response.headers.get("etag", "")
            if "no-cache" in directives:
                max_age = 0
            if etag or max_age:
                self.cache[url] = _Entry(response.content, etag, now + (max_age or 0))
            else:
                self.cache.pop(url, None)
        else:
            self.cache.pop(url, None)
        return response.content, "network"
```

An entry is the body, the ETag (the server's name for this version) and `fresh_until` (the clock time when the copy turns stale). `now < fresh_until` is the freshness test; with `max-age=0` we get `fresh_until == now`, which is never fresh, so such a response is always revalidated. On a `304` the body is **not** in the response: we reuse the stored one, which saves the transfer. A `200` after revalidation replaces the entry (the server has a new version).

Example: at `t=0` a `200` with `ETag: "v1"` and `max-age=60` is stored with `fresh_until = 60`. At `t=30`: fresh, `"cache"`. At `t=61`: stale; we send `If-None-Match: "v1"`; the server answers `304` with `max-age=60`; the entry is fresh until 121, and the answer is `"revalidated"`.

## Complexity

`O(1)` per call plus the request.

## Another way

Real caches also honour `Expires`, `Age`, `Vary` and `Last-Modified` with `If-Modified-Since`. This client covers the core: freshness, validation and `no-store`.

## Why it matters

A client that revalidates with an ETag turns a 5 MB download into a few hundred bytes (the headers of a `304`), and a client that serves fresh copies makes no request at all.
