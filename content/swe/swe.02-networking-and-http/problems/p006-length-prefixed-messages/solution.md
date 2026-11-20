## Approach

```python
import struct

LIMIT = 1_048_576


def _recv_exactly(sock, n):
    parts, got = [], 0
    while got < n:
        chunk = sock.recv(n - got)
        if chunk == b"":
            raise ConnectionError(f"connection closed after {got} of {n} bytes")
        parts.append(chunk)
        got += len(chunk)
    return b"".join(parts)


def send_message(sock, text):
    body = text.encode("utf-8")
    sock.sendall(struct.pack(">I", len(body)) + body)


def recv_message(sock):
    first = sock.recv(4)
    if first == b"":
        return None                       # clean close between messages
    header = first + _recv_exactly(sock, 4 - len(first))
    (n,) = struct.unpack(">I", header)
    if n > LIMIT:
        raise ValueError(f"message too large: {n} bytes")
    return _recv_exactly(sock, n).decode("utf-8")
```

The header is the answer to "where does this message end": every reader needs the exact same rule. We encode **before** measuring, so the length is in bytes. The first `recv` is allowed to return `b""` (the peer finished and has nothing more to say); any other close is an error. The size limit is checked before the body is read, so a lying header cannot make us allocate or wait for gigabytes.

Example: `"héllo"` is `b"h\xc3\xa9llo"`: 6 bytes. The wire holds `00 00 00 06` and then those 6 bytes.

## Complexity

`O(message length)`.

## Another way

Delimiters (a newline, section 6.5) are simpler but the text may not contain the delimiter. A length prefix works for any bytes.

## Why it matters

This is how many real protocols (databases, game servers, Redis-like systems) are framed. HTTP's `Content-Length` is the same idea.
