## Approach

```python
def recv_exactly(sock, n):
    parts = []
    got = 0
    while got < n:
        chunk = sock.recv(n - got)
        if chunk == b"":
            raise ConnectionError(f"connection closed after {got} of {n} bytes")
        parts.append(chunk)
        got += len(chunk)
    return b"".join(parts)
```

TCP is a **stream**: it keeps the order of the bytes but not the boundaries of your `send` calls (section 6.1). So a reader that needs `n` bytes must loop. Asking for `n - got` each time guarantees that we never take bytes that belong to the next message. `b""` from `recv` is the only signal that the peer closed; raising `ConnectionError` makes a half message a clear error instead of a silent short read.

Example: the writer sends `b"hel"`, then `b"lo world"`. `recv_exactly(b, 5)`: first `recv(5)` returns `hel` (got 3), then `recv(2)` returns `lo` (got 5). The rest, `b" world"`, stays for the next call.

## Complexity

`O(n)` bytes; the number of `recv` calls depends on how the network delivers.

## Another way

`sock.makefile("rb").read(n)` does the same loop (section 6.5) and returns fewer bytes only at EOF. `recv(n, socket.MSG_WAITALL)` also exists but behaves differently on Windows and with signals.

## Why it matters

Every protocol with a length (length-prefixed messages, HTTP `Content-Length`) depends on this function.
