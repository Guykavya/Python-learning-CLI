## Approach

```python
import socket


def http_get(host, port, path):
    request = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n"
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(request.encode("ascii"))
        data = b""
        while True:
            chunk = sock.recv(4096)
            if chunk == b"":
                break
            data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")
    status = int(lines[0].split(" ")[1])
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    if "content-length" in headers:
        body = body[:int(headers["content-length"])]
    return status, headers, body
```

The `Host` header is required by HTTP/1.1, and includes the port when it is not the default. `Connection: close` tells the server to close after the response, so "read until EOF" is a complete rule for the end of the message. The head is text (latin-1), the body stays bytes: a page can contain anything. Header names are case-insensitive, so lower-casing makes lookups simple.

Example: the server answers `HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\n\r\nnot found`; `status` is 404, `headers` is `{"content-length": "9"}` and `body` is `b"not found"`.

## Complexity

`O(response size)`.

## Another way

`http.client.HTTPConnection(host, port).request("GET", path)` does this and handles chunked bodies and keep-alive. This version shows the minimum.

## Why it matters

Once you have written the request and the response parser, `requests.get` is no longer magic (chapter section 7). It is these same lines plus conveniences.
