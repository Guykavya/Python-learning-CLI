import json


async def app(scope, receive, send):
    """An ASGI app: /hello -> 200 {"message": "hello"}, anything else -> 404 {"detail": "Not Found"}."""
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
