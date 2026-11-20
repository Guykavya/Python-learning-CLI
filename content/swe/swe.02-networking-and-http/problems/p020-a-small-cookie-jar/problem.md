# A small cookie jar

Chapter section 12. A cookie jar stores what servers set with `Set-Cookie` and sends it back with `Cookie`. Write

```python
class CookieJar:
    def store(self, url, set_cookie, now): ...    # one Set-Cookie header value
    def header_for(self, url, now): ...           # value of the Cookie header for a request, or ""
    def all(self, now): ...                       # list of dicts, one per live cookie
```

`now` is a number (seconds). `url` is a full URL.

**Storing.** The header is `name=value; Attr; Attr=value`. Support these attributes (case-insensitive names):

- `Path=/x`: the cookie goes only to URLs under that path. Without it, the **default path** is the request path up to (not including) its last `/`; for `/a/b` that is `/a`, for `/a` or `/` it is `/`.
- `Secure`: the cookie is sent only over `https`. A `Secure` cookie received over plain `http` is **ignored** (not stored).
- `HttpOnly`: remember it (`all()` shows `"http_only": True`); it has no effect on `header_for` (it is for browsers' scripts).
- `Max-Age=N`: expires at `now + N`. With `N <= 0` the cookie is **deleted** if it exists and not stored.

All other attributes (`Domain`, `Expires`, `SameSite`) are ignored: **every cookie is host-only**: it belongs to the exact host name of the URL that set it (no sub-domains, ports are ignored). A header without `name=` is ignored. The value may contain `=` signs. A cookie with the same host, path and name **replaces** the old one but keeps its place in creation order.

**Sending.** `header_for` returns `"a=1; b=2"` for the cookies that match the request: same host; path rule below; `Secure` only if the URL is `https`; not expired (`now < expires`). Order: **longer paths first**, equal paths in creation order.

**Path rule:** a cookie with path `/shop` matches `/shop`, `/shop/` and `/shop/cart`, but **not** `/shopping`. A cookie path ending in `/` matches everything below it.

`all(now)` returns, for each live cookie, a dict with the keys `name, value, host, path, secure, http_only, expires` (`expires` is `None` for session cookies).

## Example

```python
jar = CookieJar()
jar.store("https://shop.test/login", "sid=abc; Path=/; HttpOnly; Secure", now=0)
jar.store("https://shop.test/login", "theme=dark; Max-Age=60", now=0)
jar.header_for("https://shop.test/cart", now=10)    # "sid=abc; theme=dark"
jar.header_for("http://shop.test/cart", now=10)     # "theme=dark"
jar.header_for("https://shop.test/cart", now=60)    # "sid=abc"
```
