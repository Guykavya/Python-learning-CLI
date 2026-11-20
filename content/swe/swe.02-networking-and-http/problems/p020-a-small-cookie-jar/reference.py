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
