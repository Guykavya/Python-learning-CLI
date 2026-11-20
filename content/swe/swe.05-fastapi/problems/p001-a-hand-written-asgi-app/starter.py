import json


async def app(scope, receive, send):
    """An ASGI app: /hello -> 200 {"message": "hello"}, anything else -> 404 {"detail": "Not Found"}."""
    # TODO: build the body bytes, then send http.response.start and http.response.body.
    pass
