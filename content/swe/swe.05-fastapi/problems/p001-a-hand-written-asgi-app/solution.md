## Approach

Choose the status and the data, encode the body once, then send the two ASGI messages.

```python
import json


async def app(scope, receive, send):
    assert scope["type"] == "http"
    if scope["path"] == "/hello":
        status, data = 200, {"message": "hello"}
    else:
        status, data = 404, {"detail": "Not Found"}
    body = json.dumps(data).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
        ],
    })
    await send({"type": "http.response.body", "body": body})
```

Example: for `/hello`, `body` is `b'{"message": "hello"}'` (20 bytes), so the start message carries `(b"content-length", b"20")` and status 200.

Everything here is something FastAPI does for you: routing (`if scope["path"] == ...`), turning a dict into JSON, setting `content-type` and `content-length`, and the 404 body.

## Complexity

O(size of the body) per request.

## Another way

Keep a small routing table, `ROUTES = {"/hello": lambda: {"message": "hello"}}`, and look the path up with `ROUTES.get(path)`: a miss means 404. That is the idea of a router (section 1.2's layer diagram), and it is how Starlette's `Router` begins.
