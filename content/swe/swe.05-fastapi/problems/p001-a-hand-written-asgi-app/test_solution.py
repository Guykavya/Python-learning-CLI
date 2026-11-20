import asyncio
import inspect
import json

from solution import app


def call(path, method="GET"):
    """A fake ASGI server: run the app once and return the messages it sent."""
    sent = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {"type": "http", "method": method, "path": path, "headers": [], "query_string": b""}
    asyncio.run(app(scope, receive, send))
    return sent


def test_app_is_an_async_function_with_three_arguments():
    assert inspect.iscoroutinefunction(app), "app must be defined with 'async def': an ASGI server awaits it."
    params = list(inspect.signature(app).parameters)
    assert len(params) == 3, f"An ASGI app takes exactly (scope, receive, send); yours takes {params}."


def test_hello_sends_two_messages_in_order():
    sent = call("/hello")
    assert len(sent) == 2, (
        f"A response is two messages (http.response.start, then http.response.body); you sent {len(sent)}. "
        "Did you forget to 'await send(...)'?")
    assert sent[0]["type"] == "http.response.start", f"The first message must be http.response.start, got {sent[0].get('type')!r}."
    assert sent[1]["type"] == "http.response.body", f"The second message must be http.response.body, got {sent[1].get('type')!r}."


def test_hello_status_and_body():
    start, body = call("/hello")
    assert start["status"] == 200, f"/hello answers 200, got {start.get('status')!r}."
    assert isinstance(body["body"], bytes), "The body must be bytes: use json.dumps(...).encode()."
    assert json.loads(body["body"]) == {"message": "hello"}, f"Wrong JSON body: {body['body']!r}"


def test_headers_are_bytes_with_correct_length():
    start, body = call("/hello")
    headers = start.get("headers", [])
    assert all(isinstance(k, bytes) and isinstance(v, bytes) for k, v in headers), (
        "ASGI headers are (bytes, bytes) pairs, e.g. (b'content-type', b'application/json'), not str.")
    as_dict = dict(headers)
    assert as_dict.get(b"content-type") == b"application/json", f"content-type must be application/json, got {as_dict.get(b'content-type')!r}."
    assert as_dict.get(b"content-length") == str(len(body["body"])).encode(), (
        "content-length must be the number of BODY BYTES, as bytes: str(len(body)).encode(); "
        f"got {as_dict.get(b'content-length')!r} for a body of {len(body['body'])} bytes.")


def test_any_method_on_hello_works():
    start, _ = call("/hello", method="POST")
    assert start["status"] == 200, "The path decides, not the method: POST /hello is also 200."


def test_other_paths_are_404():
    for path in ["/", "/hello/", "/Hello", "/hello/world"]:
        start, body = call(path)
        assert start["status"] == 404, f"{path!r} is not exactly '/hello', so it must be 404, got {start['status']}."
        assert json.loads(body["body"]) == {"detail": "Not Found"}, f"The 404 body must be {{'detail': 'Not Found'}}, got {body['body']!r}."
        length = dict(start["headers"]).get(b"content-length")
        assert length == str(len(body["body"])).encode(), "The 404 also needs the right content-length."
