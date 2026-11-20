# Parse an HTTP request

Chapter sections 8.1 and 15.1: a request is text on a byte stream. Write `parse_request(data)` for a **complete request in bytes**, and the three things it needs.

```python
class BadRequest(Exception): ...

class Headers:
    def __init__(self, pairs): ...      # pairs: list of (name, value) in arrival order
    def get(self, name, default=None): ...   # case-insensitive; the first value
    def get_all(self, name): ...        # list of all values of that name, in order
    def items(self): ...                # list of (name, value) as they arrived
    def __contains__(self, name): ...   # case-insensitive

@dataclass
class Request:
    method: str; target: str; version: str; headers: Headers; body: bytes
```

`parse_request(data)` returns a `Request`:

- The request line is `METHOD SP target SP HTTP/x.y`: exactly three parts, the last starting with `HTTP/`. Anything else raises `BadRequest`.
- Header lines are `Name: value` up to the blank line (`\r\n\r\n`). The value is stripped of surrounding spaces. A line with no colon, an empty name, or a **space before the colon** (`Host : x`) raises `BadRequest`. Repeated headers are kept (each one) in order.
- Decode head text as `latin-1`. If the blank line is missing, raise `BadRequest`.
- `HTTP/1.1` **requires** a `Host` header: `BadRequest` without it. `HTTP/1.0` does not.
- The body is exactly `Content-Length` bytes after the blank line (0 if the header is absent); extra bytes after it are ignored. `Content-Length` must be digits only, else `BadRequest`; fewer bytes than announced raises `BadRequest`; two different `Content-Length` values raise `BadRequest`.

## Example

```python
raw = b"POST /notes HTTP/1.1\r\nHost: x\r\nContent-Length: 5\r\n\r\nhello"
r = parse_request(raw)
r.method, r.target, r.body      # ("POST", "/notes", b"hello")
r.headers.get("HOST")           # "x"
```
