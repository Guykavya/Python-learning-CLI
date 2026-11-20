# Notes server and resilient client

The project of chapter section 26: a small **server** written with raw sockets, and a **client** that survives a flaky network. Put both in `solution.py`.

## The server: `NotesServer`

A context manager (`with NotesServer() as server:`) that listens on `127.0.0.1` and a free port (port 0). Attributes: `server.port`, `server.base` (`"http://127.0.0.1:<port>"`), `server.connections` (TCP connections accepted) and `server.requests` (requests handled). Use plain `socket` and threads (no `http.server`). It must support **keep-alive**: many requests on one connection, `Connection: close` or HTTP/1.0 ends it. Every response has `Content-Type: application/json` and a correct `Content-Length` (bytes!).

| Request | Answer |
|---|---|
| `GET /notes` | `200` `{"notes": [{"id": 1, "text": "..."}, ...]}` |
| `POST /notes` with JSON `{"text": "hello"}` | `201`, the note `{"id": 1, "text": "hello"}`, header `Location: /notes/1`. Ids are 1, 2, 3, ... |
| `GET /notes/<id>` | `200` the note, or `404` |
| a body that is not valid JSON, not an object, or has no non-empty string `text` | `400` |
| unknown path (also `/notes/abc`) | `404` |
| a known path with a wrong method | `405` with an `Allow` header: `GET, POST` for `/notes`, `GET` for `/notes/<id>` |
| a malformed request (bad request line, bad `Content-Length`) | `400`, then the connection is closed |

Every error has the body `{"error": {"code": "<code>", "message": "<text>"}}` with the codes `bad-request`, `not-found`, `method-not-allowed`. Notes are kept in memory; several clients at the same time must not get the same id. Leaving the `with` block stops the server (the port refuses new connections shortly after).

## The client: `NotesClient`

`NotesClient(client, sleep=time.sleep, rng=random)` where `client` is an `httpx.Client` whose `base_url` is the server (or a mock transport in tests). Methods: `list_notes()` (returns the list), `get_note(id)` and `create(text, idempotency_key=None)` (return the note dict). Failures raise `RequestFailed` (with `.status` and `.attempts`). It follows the rule of problem 30: up to 4 attempts; connect errors are retried for every method; read timeouts and the statuses `429, 502, 503, 504` are retried for `GET` and for `POST` **only with an idempotency key**, with `Retry-After` honoured (at most 30 s) or full-jitter backoff (`rng.uniform(0, min(8, 0.5 * 2**k))`); other errors (`400`, `404`, `500`, ...) fail at once; the same key is sent on every attempt (header `Idempotency-Key`).

## Example

```python
with NotesServer() as server:
    with httpx.Client(base_url=server.base) as http:
        notes = NotesClient(http)
        notes.create("buy tea")        # {"id": 1, "text": "buy tea"}
        notes.list_notes()             # [{"id": 1, "text": "buy tea"}]
```
