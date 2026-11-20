## Hint 1

One call to `recv(n)` may return 1 byte or `n` bytes. What do you need to keep between calls? What value of `recv` means "closed"?

## Hint 2

Ask for what is **still missing**: `n - len(received)`. Never ask for `n` again, or you may swallow bytes of the next message.

## Hint 3

```text
parts = []; got = 0
while got < n:
    chunk = sock.recv(n - got)
    if chunk == b"": raise ConnectionError(f"connection closed after {got} of {n} bytes")
    parts.append(chunk); got += len(chunk)
return b"".join(parts)
```
