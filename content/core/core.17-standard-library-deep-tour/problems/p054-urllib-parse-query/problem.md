# Build and take apart URLs with `urllib.parse`

Gluing URLs together with `+` breaks as soon as a value contains a space, `&`, `/`, `?` or a
non-ASCII letter. `urllib.parse` does the escaping (**percent-encoding**: `&` becomes `%26`) for you:

```python
>>> urlencode({"q": "python & sql", "page": 2, "tag": ["a b", "c"]}, doseq=True)
'q=python+%26+sql&page=2&tag=a+b&tag=c'
>>> parse_qs("q=python+%26+sql&tag=a&tag=b&empty=", keep_blank_values=True)
{'q': ['python & sql'], 'tag': ['a', 'b'], 'empty': ['']}
>>> u = urlsplit("https://Example.COM/api/v1?x=1#frag")
>>> u.scheme, u.hostname, u.port, u.path, u.query
('https', 'example.com', None, '/api/v1', 'x=1')
>>> quote("a b/c"), quote("a b/c", safe="")
('a%20b/c', 'a%20b%2Fc')
```

Note: `quote` keeps `/` unescaped by default (`safe="/"`), because it is usually used for whole paths.

Write four functions in `solution.py`:

1. `build_url(base, params) -> str`: `base` (which has no `?`) plus `"?"` and the encoded `params`
   dict. A list value means the key repeats. Empty `params`: return `base` unchanged (no `?`).
2. `parse_query(url) -> dict[str, list[str]]`: the query part of a full URL as a dict of lists.
   Keys with an empty value are kept (`""`). No query: `{}`.
3. `host_port(url) -> tuple[str, int]`: the host in lower case and the port. Without an explicit port,
   use 80 for `http` and 443 for `https`. Raise `ValueError` if there is no host, or if there is no
   port and the scheme is neither `http` nor `https`.
4. `api_url(base, *segments) -> str`: `base` without a trailing `/`, then each segment escaped
   **completely** (a `/` inside a segment must become `%2F`), joined with `/`.

**Example**

```python
build_url("https://shop.example/search", {"q": "python & sql", "page": 2})
# 'https://shop.example/search?q=python+%26+sql&page=2'

parse_query("https://shop.example/search?q=python+%26+sql&tag=a&tag=b")
# {'q': ['python & sql'], 'tag': ['a', 'b']}

host_port("https://Example.COM/api")         # ('example.com', 443)
host_port("http://localhost:8080/")          # ('localhost', 8080)

api_url("http://127.0.0.1:8000/api/", "users", "a b/c")
# 'http://127.0.0.1:8000/api/users/a%20b%2Fc'
```
