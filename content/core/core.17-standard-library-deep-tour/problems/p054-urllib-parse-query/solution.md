## Approach

Every function delegates the tricky part to `urllib.parse`:

- `urlencode(..., doseq=True)` escapes keys and values for a query string (space as `+`, `&` as
  `%26`, non-ASCII as UTF-8 bytes) and repeats keys for list values.
- `parse_qs` undoes exactly that, always returning lists because any key may repeat.
- `urlsplit` separates the parts; `.hostname` is lower-cased and `.port` converted to `int` (or `None`).
- `quote(s, safe="")` escapes everything that is not a letter, digit or one of `_.-~`, so a segment can
  never add a path level (`/`), start a query (`?`) or a fragment (`#`).

## Code

```python
from urllib.parse import parse_qs, quote, urlencode, urlsplit

DEFAULT_PORTS = {"http": 80, "https": 443}


def build_url(base, params):
    if not params:
        return base
    return base + "?" + urlencode(params, doseq=True)


def parse_query(url):
    return parse_qs(urlsplit(url).query, keep_blank_values=True)


def host_port(url):
    parts = urlsplit(url)
    if not parts.hostname:
        raise ValueError(f"no host in {url!r}")
    port = parts.port
    if port is None:
        if parts.scheme not in DEFAULT_PORTS:
            raise ValueError(f"no port and unknown scheme {parts.scheme!r}")
        port = DEFAULT_PORTS[parts.scheme]
    return parts.hostname, port


def api_url(base, *segments):
    escaped = [quote(str(segment), safe="") for segment in segments]
    return "/".join([base.rstrip("/"), *escaped])
```

## Complexity

All linear in the length of the URL.

## Another way

`urljoin(base, relative)` resolves a link the way a browser does, which surprises many people:
`urljoin("http://x.com/api/v1", "users")` gives `http://x.com/api/users` (the last segment is
replaced, because `v1` has no trailing `/`) and `urljoin(..., "/users")` jumps to the site root.
That is right for following links in a web page, and wrong for building API paths, which is why
`api_url` joins escaped segments itself. `parse_qsl` returns a list of `(key, value)` pairs instead of a
dict, keeping the original order of repeated keys.
