## Approach

Look at the path, build a status and a text, encode the text to bytes, call `start_response`, return the bytes in a list.

```python
from urllib.parse import parse_qs


def app(environ, start_response):
    if environ["PATH_INFO"] == "/hello":
        query = parse_qs(environ.get("QUERY_STRING", ""))
        name = query.get("name", ["world"])[0]
        status, text = "200 OK", f"Hello, {name}"
    else:
        status, text = "404 Not Found", "Not Found"
    body = text.encode("utf-8")
    start_response(status, [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ])
    return [body]
```

Example: for `/hello?name=Zoë` the text has 10 characters but the UTF-8 body has 11 bytes, so `Content-Length` is `11`. Measuring the encoded `body`, not `text`, is what keeps the header right.

This is the contract Flask implements: `app.wsgi_app(environ, start_response)` builds a `Request` from `environ`, finds the view, turns its return value into a `Response`, and calls `start_response` for you.

## Complexity

`O(length of the query string)`.

## Another way

`wsgiref.simple_server.make_server("127.0.0.1", 0, app)` would run this app as a real server. Or use `werkzeug.wrappers.Request(environ)` to read the query as `request.args`: that is exactly what Flask does.
