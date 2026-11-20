## Hint 1

Look again at the first program of section 1.2. What are the two messages, and what keys does each one have? What is the only thing that changes between `/hello` and any other path?

## Hint 2

Decide `status` and the Python dict first, then turn the dict into bytes **once**, so the `content-length` is computed from the real bytes you send.

## Hint 3

```text
if scope["path"] == "/hello": status, data = 200, {"message": "hello"}
else:                         status, data = 404, {"detail": "Not Found"}
body = json.dumps(data).encode()
await send({"type": "http.response.start", "status": status,
            "headers": [(b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode())]})
await send({"type": "http.response.body", "body": body})
```
