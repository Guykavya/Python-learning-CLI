## Approach

```python
from http import HTTPStatus


def build_response(status, body="", content_type="text/plain; charset=utf-8"):
    try:
        phrase = HTTPStatus(status).phrase
    except ValueError:
        phrase = "Unknown"
    if isinstance(body, str):
        body = body.encode("utf-8")
    lines = [f"HTTP/1.1 {status} {phrase}"]
    if status in (204, 304) or 100 <= status < 200:
        if body:
            raise ValueError(f"a {status} response has no body")
        return ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")
    lines.append(f"Content-Type: {content_type}")
    lines.append(f"Content-Length: {len(body)}")
    return ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1") + body
```

`Content-Length: len(body)` is taken **after** encoding, so `"é"` counts 2. If the number were smaller than the real size, a client would stop reading early and treat the rest as the start of the next response; if bigger, it would wait for bytes that never come. The no-body statuses must not carry a length or content type, because clients are told to ignore a body for them.

Example: `build_response(404, "é")` gives `b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 2\r\n\r\n\xc3\xa9"`.

## Complexity

`O(len(body))`.

## Another way

`http.server` does this for you with `send_response`, `send_header` and `end_headers`. Building the bytes yourself shows that nothing more is on the wire.

## Why it matters

A wrong `Content-Length` is one of the most common server bugs: pages that hang forever or are cut off, only for non-ASCII text.
