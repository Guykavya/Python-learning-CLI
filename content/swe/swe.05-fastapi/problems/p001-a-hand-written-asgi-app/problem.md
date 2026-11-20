# A hand-written ASGI app

Chapter sections 1.1 and 1.2. Before using FastAPI, write a tiny **ASGI application by hand**, with no framework at all, so that you see what FastAPI does for you.

In `solution.py` write

```python
async def app(scope, receive, send):
    ...
```

Rules:

- Only HTTP is handled: `scope["type"]` is `"http"`. (You may `assert` it.)
- If `scope["path"]` is exactly `"/hello"` (any method), answer **200** with the JSON body `{"message": "hello"}`.
- For any other path answer **404** with the JSON body `{"detail": "Not Found"}` (the same body FastAPI uses).
- A response is **two messages** sent with `await send(...)`:
  1. `{"type": "http.response.start", "status": ..., "headers": [...]}` where `headers` is a list of `(name, value)` pairs of **bytes**: `(b"content-type", b"application/json")` and `(b"content-length", b"<number of body bytes>")`.
  2. `{"type": "http.response.body", "body": <the JSON as bytes>}`.
- Build the body with `json.dumps(...).encode()`, so `content-length` is `str(len(body)).encode()`.

You do not need to call `receive` (a GET has no body), but your function must accept it.

The tests act as the "fake server" of section 1.2: they build a `scope`, pass a `receive` and a `send` that records the messages, and run `asyncio.run(app(scope, receive, send))`.

## Example

```text
scope path "/hello"  -> sent messages:
  {"type": "http.response.start", "status": 200,
   "headers": [(b"content-type", b"application/json"), (b"content-length", b"20")]}
  {"type": "http.response.body", "body": b'{"message": "hello"}'}

scope path "/nope"   -> status 404, body b'{"detail": "Not Found"}'
```

(`json.dumps({"message": "hello"})` is the 20 characters `{"message": "hello"}`.)
