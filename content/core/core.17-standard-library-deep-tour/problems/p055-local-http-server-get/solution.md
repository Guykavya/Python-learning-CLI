## Approach

**Server.** `HTTPServer` accepts connections and creates one `KVHandler` per request; the handler's
`do_GET` / `do_POST` method writes the answer. All answers go through one helper that sends status,
headers and a JSON body with the right `Content-Length`. Shared data lives on the server object
(`server.store`), which every handler reaches through `self.server`. The key is taken from the path
**without** the query string and percent-decoded.

**Lifecycle.** Port `0` lets the operating system choose a free port, so tests never collide with
another program. `serve_forever` runs in a daemon thread (a daemon thread cannot keep the program alive
by accident). Stopping is two steps: `shutdown()` asks the loop to stop and waits for it;
`server_close()` releases the listening socket. Joining the thread confirms it ended.

**Client.** `urlopen` returns normally only for 1xx-3xx answers; for 4xx/5xx it raises `HTTPError`,
which is itself a response object with `.code` and `.read()`. Catching it lets the caller deal with
"not found" as data. The `timeout` turns a silent server into a `TimeoutError` instead of a hang.

## Code

```python
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

PREFIX = "/items/"


class KVHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _key(self):
        path = urlsplit(self.path).path
        if path.startswith(PREFIX) and len(path) > len(PREFIX):
            return unquote(path[len(PREFIX):])
        return None

    def do_GET(self):
        if urlsplit(self.path).path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        key = self._key()
        store = self.server.store
        if key is None or key not in store:
            self._send_json(404, {"error": "not found"})
        else:
            self._send_json(200, {"key": key, "value": store[key]})

    def do_POST(self):
        key = self._key()
        if key is None:
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except ValueError:
            data = None
        if not isinstance(data, dict) or "value" not in data:
            self._send_json(400, {"error": "bad request"})
            return
        self.server.store[key] = data["value"]
        self._send_json(201, {"key": key, "value": data["value"]})

    def log_message(self, format, *args):
        pass


def start_server(store):
    server = HTTPServer(("127.0.0.1", 0), KVHandler)
    server.store = store
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    return server, thread, f"http://{host}:{port}"


def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def _read(response):
    return json.loads(response.read().decode("utf-8"))


def get_json(url, timeout=5):
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.status, _read(response)
    except HTTPError as err:
        with err:
            return err.code, _read(err)


def post_json(url, payload, timeout=5):
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, _read(response)
    except HTTPError as err:
        with err:
            return err.code, _read(err)
```

## Complexity

Each request is O(size of the body) plus a dict lookup. `HTTPServer` handles **one request at a
time**; `ThreadingHTTPServer` (same module) starts a thread per request when several clients must be
served at once.

## Another way

For quick experiments, `python -m http.server 8000 --bind 127.0.0.1` serves the files of the current
folder with no code at all. Real web applications use a framework (Flask, FastAPI) on top of a
production server; `http.server` is meant for tests, tools and learning, and its documentation warns
that it is not hardened for the public internet. On the client side, the third-party `requests`
library is friendlier, but `urllib` is always there.
