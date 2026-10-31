## Hint 1

Which function turns a dict into `a=1&b=2`, and which keyword makes a list value repeat the key? Which
function splits a URL into scheme, host, port, path and query? Which attribute of the result gives a
lower-case host and an `int` port?

## Hint 2

- `build_url`: `base + "?" + urlencode(params, doseq=True)`, but only if `params` is not empty.
- `parse_query`: `parse_qs(urlsplit(url).query, keep_blank_values=True)`.
- `host_port`: `parts = urlsplit(url)`; use `parts.hostname` and `parts.port`, then a dict
  `{"http": 80, "https": 443}` for the default.
- `api_url`: `quote(segment, safe="")` for every segment.

## Hint 3

```
host_port(url):
    parts = urlsplit(url)
    if not parts.hostname: raise ValueError
    port = parts.port
    if port is None:
        if parts.scheme not in DEFAULTS: raise ValueError
        port = DEFAULTS[parts.scheme]
    return parts.hostname, port

api_url(base, *segments) = "/".join([base.rstrip("/")] + [quote(s, safe="") for s in segments])
```
