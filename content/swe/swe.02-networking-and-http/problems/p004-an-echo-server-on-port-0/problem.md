# An echo server on port 0

Write `start_echo_server()` that starts a TCP server **in a background thread** and returns `(server_socket, port)`.

- It listens on `127.0.0.1` on a **free port chosen by the operating system** (port 0, then `getsockname()[1]`, chapter section 3.3). Never a fixed number such as 5000.
- For every message (every `recv`), it sends back the same bytes **in upper case**, until the client closes the connection.
- It serves **several clients at the same time**: a second client must not wait for the first to finish.
- The thread must be a daemon thread. When the test closes `server_socket`, the accept loop must end quietly, and the port must stop accepting connections within a fraction of a second.

## Example

```python
import socket
server, port = start_echo_server()
with socket.create_connection(("127.0.0.1", port)) as c:
    c.sendall(b"hello")
    print(c.recv(100))        # b'HELLO'
server.close()
```
