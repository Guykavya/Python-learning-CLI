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
        path = urlsplit(self.path).path            # drop ?query
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
        except ValueError:                          # json.JSONDecodeError and bad UTF-8
            data = None
        if not isinstance(data, dict) or "value" not in data:
            self._send_json(400, {"error": "bad request"})
            return
        self.server.store[key] = data["value"]
        self._send_json(201, {"key": key, "value": data["value"]})

    def log_message(self, format, *args):
        pass                                        # keep test output clean


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
