# Testing network code without network

A unit test that touches the network is slow, flaky and sometimes dangerous. Two defences work
together: **inject** a fake client so the logic never needs a socket, and install a **guard** that
fails the test loudly if a real socket is ever opened.

In `solution.py` write:

```python
def default_get(url): ...                    # real HTTP GET, returns (status_code, body_text)
def fetch_title(url, http_get=None): ...     # logic on top of an http_get(url) function
```

**`default_get(url)`** uses `urllib.request.urlopen(url, timeout=5)` (call it as
`urllib.request.urlopen`, after `import urllib.request`). It returns `(response.status, text)` with the
body decoded as UTF-8. When urllib raises `urllib.error.HTTPError` (404, 500, ...) return
`(error.code, "")` instead of raising.

**`fetch_title(url, http_get=None)`**: if `http_get` is `None`, use `default_get` (look it up when the
function runs, not in the signature). Then call `http_get(url)` **once** and:

- status 200: parse the body as JSON and return its `"title"` value; invalid JSON raises
  `ValueError(f"bad JSON from {url}")`;
- status 404: return `None`;
- any other status: raise `RuntimeError(f"HTTP {status} for {url}")`.

The checker installs a guard that replaces `socket.socket`, `socket.create_connection` and
`socket.getaddrinfo` with functions that raise `NetworkBlocked`. No test is allowed to reach a real
socket.

**Example**

```python
def fake_get(url):
    return 200, '{"title": "Hello"}'

fetch_title("http://example.test/a", http_get=fake_get)   # 'Hello'
```
