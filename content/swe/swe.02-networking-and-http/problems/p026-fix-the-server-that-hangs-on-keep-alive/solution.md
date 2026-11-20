## Approach

The bug is one loop. The original reads the body with "keep calling `recv` until it returns `b""`": that only happens when the client closes the connection. A keep-alive client does **not** close; it waits for the answer, and the server waits for it to close: a deadlock.

```python
def serve_connection(conn):
    """Serve requests on one connection until the client closes it.
    Every request gets the answer: 200, with a body holding the number of body bytes received."""
    buf = b""
    while True:
        while b"\r\n\r\n" not in buf:
            chunk = conn.recv(4096)
            if not chunk:
                return
            buf += chunk
        head, _, buf = buf.partition(b"\r\n\r\n")
        length = 0
        for line in head.split(b"\r\n")[1:]:
            name, _, value = line.partition(b":")
            if name.strip().lower() == b"content-length":
                length = int(value)
        while len(buf) < length:          # read exactly Content-Length bytes
            chunk = conn.recv(4096)
            if not chunk:
                return                    # the client left in the middle of a body
            buf += chunk
        body, buf = buf[:length], buf[length:]
        reply = str(len(body)).encode()
        conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(reply) + reply)
```

The fix reads exactly `length` bytes: first what is already in `buf`, then more from `recv` only while something is missing. After taking the body, the rest of `buf` (possibly the whole next request, if the client was in a hurry, so-called **pipelining**) stays in `buf` for the next iteration of the outer loop. Without this step the second request would be lost.

Example: a client sends `POST` with `Content-Length: 5` and `hello`, and waits. `buf` already holds all 5 bytes after the head; the new loop reads nothing more; the answer `5` goes out at once.

## Complexity

`O(bytes received)`.

## Another way

`conn.makefile("rb")` and `reader.read(length)` do the "exactly n bytes" loop for you, including the buffering (chapter section 15.1 uses it).

## Why it matters

"Read until the socket closes" is the HTTP/1.0 way (`Connection: close`). HTTP/1.1 keeps connections open, so **every** message needs its own end marker: here, `Content-Length`.
