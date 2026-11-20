## Approach

```python
from urllib.parse import urlsplit


def _default_path(path):
    if not path.startswith("/") or path.count("/") == 1:
        return "/"
    return path[:path.rindex("/")]


def _path_match(cookie_path, request_path):
    if cookie_path == request_path:
        return True
    if request_path.startswith(cookie_path):
        return cookie_path.endswith("/") or request_path[len(cookie_path)] == "/"
    return False


class CookieJar:
    def __init__(self):
        self._cookies = {}          # (host, path, name) -> dict; insertion order = creation order

    def store(self, url, set_cookie, now):
        parts = urlsplit(url)
        host, https = parts.hostname, parts.scheme == "https"
        pieces = [p.strip() for p in set_cookie.split(";")]
        name, eq, value = pieces[0].partition("=")
        name, value = name.strip(), value.strip()
        if not eq or not name:
            return
        path = _default_path(parts.path or "/")
        secure = http_only = False
        expires = None
        for attr in pieces[1:]:
            key, _, val = attr.partition("=")
            key, val = key.strip().lower(), val.strip()
            if key == "path" and val.startswith("/"):
                path = val
            elif key == "secure":
                secure = True
            elif key == "httponly":
                http_only = True
            elif key == "max-age":
                try:
                    expires = now + int(val)
                except ValueError:
                    pass
        if secure and not https:
            return                   # a Secure cookie cannot be set over plain http
        key = (host, path, name)
        if expires is not None and expires <= now:
            self._cookies.pop(key, None)
            return
        self._cookies[key] = {"name": name, "value": value, "host": host, "path": path,
                              "secure": secure, "http_only": http_only, "expires": expires}

    def _live(self, now):
        for key in [k for k, c in self._cookies.items() if c["expires"] is not None and now >= c["expires"]]:
            del self._cookies[key]
        return list(self._cookies.values())

    def header_for(self, url, now):
        parts = urlsplit(url)
        host, https, path = parts.hostname, parts.scheme == "https", parts.path or "/"
        chosen = [c for c in self._live(now)
                  if c["host"] == host and (https or not c["secure"]) and _path_match(c["path"], path)]
        chosen.sort(key=lambda c: -len(c["path"]))          # stable: equal paths keep creation order
        return "; ".join(f"{c['name']}={c['value']}" for c in chosen)

    def all(self, now):
        return [dict(c) for c in self._live(now)]
```

The jar is a dictionary `(host, path, name) -> cookie`. Assigning to an existing key replaces the value but keeps the position, which gives "replace, keep creation order" for free. Expiry is checked when the jar is read, so no timer is needed. The path rule has one trap: `startswith` alone would send a `/shop` cookie to `/shopping`; the extra test (`cookie_path` ends with `/` or the next character is `/`) makes the match respect path **segments**. `Secure` over `http` is refused at storing time (the browser rule), and `https` is checked again when sending.

Example from the statement: at `now=10` both cookies are valid. Over `http` the `Secure` one is skipped: `"theme=dark"`. At `now=60` `theme` has expired (`60 >= 0 + 60`): `"sid=abc"`.

## Complexity

`O(number of cookies)` per request.

## Another way

Python's `http.cookiejar` and `http.cookies` implement the full rules (`Domain`, `Expires`, `SameSite`, public suffixes). This problem builds the core to show how little is needed, and why `Domain` and `Secure` matter.

## Why it matters

Cookies carry login sessions. A jar that sends a `Secure` cookie over `http`, or `/shopping` cookies to `/shop`, leaks them.
