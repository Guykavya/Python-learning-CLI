## Hint 1

What would you need to know to cut the stream into messages? Put that in front of every message, in a fixed number of bytes. Which `struct` format is "unsigned 32-bit, big-endian"?

## Hint 2

Encode the text **first**, then take `len()` of the bytes. Reading is two steps: read exactly 4 bytes (the header), then exactly `n` bytes (the body). The first step is special: closing there is normal.

## Hint 3

```text
send: body = text.encode("utf-8"); sock.sendall(struct.pack(">I", len(body)) + body)
recv: first = read up to 4 bytes (loop): if you got 0 bytes and the peer closed -> return None
      if 1..3 bytes then closed -> ConnectionError
      n = struct.unpack(">I", header)[0]; if n > LIMIT: ValueError
      body = recv_exactly(n); return body.decode("utf-8")
```
