## Hint 1

Where in the function does the server wait for the client to close the connection? Look for a loop that only stops at `b""`. Why does it never stop with a keep-alive client?

## Hint 2

The head told you the body length. What is the right condition to stop reading the body? Remember that some body bytes may already be in `buf` from the same `recv` that brought the head.

## Hint 3

```text
while len(buf) < length:
    chunk = conn.recv(4096)
    if not chunk: return           # the client closed early
    buf += chunk
body, buf = buf[:length], buf[length:]       # anything after the body belongs to the next request
```
