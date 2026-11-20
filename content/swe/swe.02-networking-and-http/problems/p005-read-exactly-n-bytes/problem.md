# Read exactly n bytes

`sock.recv(n)` returns **up to** `n` bytes, often fewer (chapter section 6.1). Write

```python
recv_exactly(sock, n)
```

that returns **exactly** `n` bytes, calling `recv` as many times as needed.

- `n == 0` returns `b""` without reading.
- If the other side closes the connection (`recv` returns `b""`) before `n` bytes have arrived, raise `ConnectionError`. The message must say how many bytes arrived and how many were expected (for example `"connection closed after 3 of 10 bytes"`).
- Never read **more** than `n` bytes: whatever comes after belongs to the next message and must stay in the socket.

## Example

```python
import socket
a, b = socket.socketpair()
a.sendall(b"hel"); a.sendall(b"lo world")
print(recv_exactly(b, 5))      # b'hello'
print(recv_exactly(b, 6))      # b' world'
```
