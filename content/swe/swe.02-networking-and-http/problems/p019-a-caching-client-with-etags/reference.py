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
