## Hint 1

Split the work: first `start_server` / `stop_server` (the tests cannot run without them), then
`do_GET`, then `get_json`, then `do_POST` and `post_json`. For each request, the handler must send
three things in order: what are they, and which methods send them?

## Hint 2

- Write one helper `_send_json(self, status, payload)`: `json.dumps(...).encode("utf-8")`,
  `send_response`, two `send_header` calls, `end_headers`, `wfile.write`.
- The key: `path = urlsplit(self.path).path`; if it starts with `"/items/"` and is longer, the key is
  `unquote(path[len("/items/"):])`.
- POST body: `length = int(self.headers.get("Content-Length", 0))`, then `self.rfile.read(length)`;
  `json.loads` raises `ValueError` for bad JSON.
- Client: `try: with urlopen(url, timeout=timeout) as r: return r.status, json.loads(r.read())`
  and `except HTTPError as err: return err.code, json.loads(err.read())`.

## Hint 3

```
start_server(store):
    server = HTTPServer(("127.0.0.1", 0), KVHandler)
    server.store = store
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_address[1]}"

stop_server(server, thread): server.shutdown(); server.server_close(); thread.join(timeout=5)

post_json(url, payload, timeout):
    req = Request(url, data=json.dumps(payload).encode("utf-8"),
                  headers={"Content-Type": "application/json"}, method="POST")
    same try/except as get_json, with urlopen(req, timeout=timeout)
```
