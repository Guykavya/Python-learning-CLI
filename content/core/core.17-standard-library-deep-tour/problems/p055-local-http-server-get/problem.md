# A tiny JSON server and client on `127.0.0.1`

The standard library has both sides of HTTP: `http.server` to **serve** requests and
`urllib.request` to **send** them. In this problem you write a small key-value service and a client
for it, and the tests run both in the same process: the server in a background thread, on your own
computer only (no internet is ever used).

## How the server side works

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):                 # called once per GET request
        body = b'{"hello": "world"}'
        self.send_response(200)                               # status line
        self.send_header("Content-Type", "application/json")  # headers...
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()                                    # blank line
        self.wfile.write(body)                                # the body (bytes)

server = HTTPServer(("127.0.0.1", 0), Handler)   # port 0: the OS picks a free port
port = server.server_address[1]                  # ...which you read back here
```

- Inside a handler, `self.path` is the path plus query (`"/items/lang?x=1"`), `self.headers` the request
  headers, `self.rfile` the request body (read exactly `Content-Length` bytes) and `self.server` the
  server object (a good place to keep shared data).
- `server.serve_forever()` blocks, so run it in a `threading.Thread(..., daemon=True)`.
- To stop: `server.shutdown()` (ends the `serve_forever` loop; it waits for it, so never call it if
  the loop was never started), then `server.server_close()` (frees the port).
- `127.0.0.1` means "this computer only": nobody on the network can reach the server.
- By default the handler prints a log line for every request; override `log_message` to stay quiet.

## How the client side works

`urlopen(url_or_request, timeout=5)` returns a response with `.status` and `.read()` (bytes). For a
status of 400 or more it **raises** `urllib.error.HTTPError`, which also has `.code` and `.read()`.
A `Request(url, data=bytes, headers={...}, method="POST")` sends a body. **Always pass a timeout**:
without one, a server that never answers hangs your program forever.

## Your task

In `solution.py` write:

1. `class KVHandler(BaseHTTPRequestHandler)`, using the dict `self.server.store`:
   - `GET /items/<key>`: `200` and `{"key": key, "value": value}`, or `404` and `{"error": "not found"}`.
   - `POST /items/<key>` with a JSON body `{"value": ...}`: store it, answer `201` and
     `{"key": key, "value": value}`. A body that is not JSON, or has no `"value"`: `400` and
     `{"error": "bad request"}`.
   - `GET /health`: `200` and `{"status": "ok"}`.
   - Any other path: `404` and `{"error": "not found"}`.
   - Ignore the query string (`/items/lang?x=1` is key `lang`) and decode `%20` etc. in the key
     (`urllib.parse.unquote`). Every answer is JSON with `Content-Type: application/json`.
   - Silence `log_message`.
2. `start_server(store) -> tuple[HTTPServer, Thread, str]`: an `HTTPServer` on `("127.0.0.1", 0)`
   with `server.store = store`, `serve_forever` running in a started daemon thread, and the base URL
   `"http://127.0.0.1:<port>"`.
3. `stop_server(server, thread)`: `shutdown()`, `server_close()`, then `thread.join(timeout=5)`.
4. `get_json(url, timeout=5) -> tuple[int, object]` and `post_json(url, payload, timeout=5) -> tuple[int, object]`:
   send the request with the timeout and return `(status, decoded_json)`. **Do not raise** for 4xx/5xx
   answers: catch `HTTPError` and return its code and JSON body.

**Example**

```python
store = {"lang": "python"}
server, thread, base = start_server(store)
try:
    get_json(base + "/items/lang")                      # (200, {'key': 'lang', 'value': 'python'})
    get_json(base + "/items/nope")                      # (404, {'error': 'not found'})
    post_json(base + "/items/year", {"value": 2025})    # (201, {'key': 'year', 'value': 2025})
    store                                               # {'lang': 'python', 'year': 2025}
finally:
    stop_server(server, thread)
```
