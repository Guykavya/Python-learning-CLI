import json
import random
import socket
import threading
import time
from urllib.parse import urlsplit

import httpx

# ---------------------------------------------------------------- the server

REASONS = {200: "OK", 201: "Created", 400: "Bad Request", 404: "Not Found", 405: "Method Not Allowed",
           500: "Internal Server Error"}
MAX_LINE = 65_536
MAX_BODY = 1_000_000


class _BadRequest(Exception):
    pass


def _read_request(reader):
    line = reader.readline(MAX_LINE)
    if line == b"":
        return None
    parts = line.decode("latin-1").rstrip("\r\n").split(" ")
    if len(parts) != 3 or not parts[2].startswith("HTTP/"):
        raise _BadRequest("malformed request line")
    headers = {}
    while True:
        raw = reader.readline(MAX_LINE)
        if raw in (b"\r\n", b"\n"):
            break
        name, colon, value = raw.decode("latin-1").partition(":")
        if raw == b"" or not colon:
            raise _BadRequest("malformed header")
        headers[name.strip().lower()] = value.strip()
    try:
        length = int(headers.get("content-length", "0"))
    except ValueError:
        raise _BadRequest("Content-Length is not a number") from None
    if not 0 <= length <= MAX_BODY:
        raise _BadRequest("bad Content-Length")
    body = reader.read(length)
    if len(body) < length:
        raise _BadRequest("body cut short")
    return parts[0].upper(), urlsplit(parts[1]).path, parts[2], headers, body


def _response(status, obj, keep_alive, extra=None):
    body = json.dumps(obj).encode("utf-8")
    lines = [f"HTTP/1.1 {status} {REASONS.get(status, 'Unknown')}",
             "Content-Type: application/json",
             f"Content-Length: {len(body)}",
             f"Connection: {'keep-alive' if keep_alive else 'close'}"]
    lines += [f"{k}: {v}" for k, v in (extra or {}).items()]
    return "\r\n".join(lines).encode("latin-1") + b"\r\n\r\n" + body


def _error(status, code, message, extra=None):
    return status, {"error": {"code": code, "message": message}}, extra or {}


class NotesServer:
    def __init__(self):
        self.notes = []
        self.connections = 0
        self.requests = 0
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._listener = socket.socket()
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen()
        self._listener.settimeout(0.1)
        self.port = self._listener.getsockname()[1]
        self.base = f"http://127.0.0.1:{self.port}"

    def __enter__(self):
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        self._listener.close()

    def _accept_loop(self):
        while not self._stop.is_set():
            try:
                conn, _ = self._listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            with self._lock:
                self.connections += 1
            threading.Thread(target=self._serve_connection, args=(conn,), daemon=True).start()

    def _serve_connection(self, conn):
        conn.settimeout(5)
        with conn, conn.makefile("rb") as reader:
            while True:
                try:
                    request = _read_request(reader)
                except _BadRequest as exc:
                    status, obj, extra = _error(400, "bad-request", str(exc))
                    conn.sendall(_response(status, obj, False, extra))
                    return
                except OSError:
                    return
                if request is None:
                    return
                method, path, version, headers, body = request
                with self._lock:
                    self.requests += 1
                keep_alive = headers.get("connection", "").lower() != "close" and version == "HTTP/1.1"
                try:
                    status, obj, extra = self._handle(method, path, body)
                except Exception:
                    status, obj, extra = _error(500, "internal-error", "something went wrong")
                conn.sendall(_response(status, obj, keep_alive, extra))
                if not keep_alive:
                    return

    def _handle(self, method, path, body):
        if path == "/notes":
            if method == "GET":
                with self._lock:
                    return 200, {"notes": list(self.notes)}, {}
            if method == "POST":
                try:
                    data = json.loads(body)
                except ValueError:
                    return _error(400, "bad-request", "the body is not valid JSON")
                text = data.get("text") if isinstance(data, dict) else None
                if not isinstance(text, str) or not text.strip():
                    return _error(400, "bad-request", "the body must be an object with a non-empty text")
                with self._lock:
                    note = {"id": len(self.notes) + 1, "text": text}
                    self.notes.append(note)
                return 201, note, {"Location": f"/notes/{note['id']}"}
            return _error(405, "method-not-allowed", f"{method} is not allowed here", {"Allow": "GET, POST"})
        prefix = "/notes/"
        if path.startswith(prefix) and path[len(prefix):].isascii() and path[len(prefix):].isdigit():
            note_id = int(path[len(prefix):])
            if method != "GET":
                return _error(405, "method-not-allowed", f"{method} is not allowed here", {"Allow": "GET"})
            with self._lock:
                if 1 <= note_id <= len(self.notes):
                    return 200, self.notes[note_id - 1], {}
            return _error(404, "not-found", f"no note {note_id}")
        return _error(404, "not-found", f"no such path: {path}")


# ---------------------------------------------------------------- the client

class RequestFailed(Exception):
    def __init__(self, message, status=None, attempts=1):
        super().__init__(message)
        self.status = status
        self.attempts = attempts


RETRY_STATUSES = {429, 502, 503, 504}
NEVER_SENT = (httpx.ConnectError, httpx.ConnectTimeout)
BASE, CAP, MAX_WAIT = 0.5, 8.0, 30.0


def _wait(attempt_index, response, rng):
    if response is not None:
        value = response.headers.get("retry-after", "").strip()
        if value.isascii() and value.isdigit():
            return min(float(value), MAX_WAIT)
    return rng.uniform(0, min(CAP, BASE * 2 ** attempt_index))


def _request(client, method, url, repeatable, attempts, sleep, rng, **kwargs):
    for attempt in range(attempts):
        last = attempt == attempts - 1
        response = None
        try:
            response = client.request(method, url, **kwargs)
        except httpx.TransportError as exc:
            read_error = isinstance(exc, (httpx.ReadTimeout, httpx.ReadError, httpx.RemoteProtocolError))
            if last or not (isinstance(exc, NEVER_SENT) or (repeatable and read_error)):
                raise RequestFailed(f"{method} {url} failed: {type(exc).__name__}", None, attempt + 1) from exc
        else:
            if response.status_code < 400:
                return response
            if last or not repeatable or response.status_code not in RETRY_STATUSES:
                raise RequestFailed(f"{method} {url} -> {response.status_code}", response.status_code, attempt + 1)
        sleep(_wait(attempt, response, rng))


class NotesClient:
    def __init__(self, client, sleep=time.sleep, rng=random, attempts=4):
        self.client = client
        self.sleep = sleep
        self.rng = rng
        self.attempts = attempts

    def _json(self, response, method, url):
        try:
            return response.json()
        except ValueError:
            raise RequestFailed(f"{method} {url}: the body is not JSON", response.status_code) from None

    def list_notes(self):
        r = _request(self.client, "GET", "/notes", True, self.attempts, self.sleep, self.rng)
        return self._json(r, "GET", "/notes")["notes"]

    def get_note(self, note_id):
        url = f"/notes/{note_id}"
        r = _request(self.client, "GET", url, True, self.attempts, self.sleep, self.rng)
        return self._json(r, "GET", url)

    def create(self, text, idempotency_key=None):
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        r = _request(self.client, "POST", "/notes", bool(idempotency_key), self.attempts, self.sleep, self.rng,
                     json={"text": text}, headers=headers)
        return self._json(r, "POST", "/notes")
