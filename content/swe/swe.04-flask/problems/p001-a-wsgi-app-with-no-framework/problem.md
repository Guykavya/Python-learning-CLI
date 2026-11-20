# A WSGI app with no framework

Chapter section 1.2. Flask is, at its heart, a **WSGI application**: a callable `app(environ, start_response)` that the server calls once per request. Write one by hand, without Flask, so you see what the framework does for you.

In `solution.py` define `app(environ, start_response)`:

- `GET /hello` answers **200** and the text `Hello, <name>`, where `<name>` is the `name` query parameter (`/hello?name=Asha` gives `Hello, Asha`). Without `name`, use `world`. The value is URL-decoded (`name=Asha%20K` gives `Asha K`).
- Any other path (including `/hello/`) answers **404** with the text `Not Found`.
- `start_response(status, headers)` takes the status **as a string** (`"200 OK"`, `"404 Not Found"`) and the headers **as a list of `(name, value)` tuples**. Send `Content-Type: text/plain; charset=utf-8` and a correct `Content-Length` (the number of **bytes**, not characters).
- The return value is an **iterable of bytes** (for example a list with one `bytes` object), never a `str`.

Useful: `environ["PATH_INFO"]` is the path, `environ["QUERY_STRING"]` the raw query string, and `urllib.parse.parse_qs` decodes it.

## Example

```python
environ = {"PATH_INFO": "/hello", "QUERY_STRING": "name=Asha", ...}
body = app(environ, start_response)        # start_response("200 OK", [...])
b"".join(body)                             # b"Hello, Asha"
```

The tests build a full `environ` with `wsgiref.util.setup_testing_defaults`, so you do not need a server.
