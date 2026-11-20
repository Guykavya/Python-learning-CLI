## Hint 1

Which three socket calls make a listening socket? (`bind`, `listen`, and what comes before them?) What value of the port asks the operating system to choose?

## Hint 2

`accept()` blocks until a client arrives. If the server handles that client inside the accept loop, a second client waits. What can handle each client independently?

## Hint 3

```text
srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen()
port = srv.getsockname()[1]
thread: loop { conn, _ = srv.accept()   (stop on OSError: the socket was closed)
               start a thread for conn: while data := conn.recv(4096): conn.sendall(data.upper()) }
return srv, port
```

Tip: `close()` from another thread does not wake a blocked `accept()` on Linux. Give the listening socket a short timeout (`settimeout(0.1)`) and treat `socket.timeout` as "look again".
