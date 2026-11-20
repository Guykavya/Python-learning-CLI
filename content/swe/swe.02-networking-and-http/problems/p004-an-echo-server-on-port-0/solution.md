## Approach

```python
import socket
import threading


def _serve_client(conn):
    with conn:
        while True:
            try:
                data = conn.recv(4096)
            except OSError:
                return
            if not data:
                return
            conn.sendall(data.upper())


def _accept_loop(server):
    while True:
        try:
            conn, _ = server.accept()
        except socket.timeout:          # wake up regularly: a closed server socket is noticed here
            continue
        except OSError:                 # the listening socket was closed
            return
        conn.settimeout(None)
        threading.Thread(target=_serve_client, args=(conn,), daemon=True).start()


def start_echo_server():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen()
    server.settimeout(0.1)
    port = server.getsockname()[1]
    threading.Thread(target=_accept_loop, args=(server,), daemon=True).start()
    return server, port
```

Port 0 means "any free port", so two servers (or two test runs at once) never fight for one number. `getsockname()` tells you which one you got. On Linux a thread blocked in `accept()` does not notice that another thread closed the socket, so the loop waits at most 0.1 s per round (`settimeout`) and then looks again: after `server.close()` the next `accept` raises `OSError` and the loop ends. A new thread per client lets the accept loop go back to `accept()` at once. `recv` returning `b""` means the client closed its side.

Example: a client sends `b"hello"`; `recv` returns it; `b"hello".upper()` is `b"HELLO"`; `sendall` sends it back.

## Complexity

`O(message length)` per message; one thread per connection.

## Another way

`socketserver.ThreadingTCPServer` does the accept loop and the threads for you (core.17). Writing the loop by hand shows what it does.

## Why it matters

Every network test in this course starts a server on port 0. A hard-coded port is the usual reason tests fail on a second run or on a colleague's machine.
