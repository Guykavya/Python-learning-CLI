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
        body = buf
        buf = b""
        while True:                       # read the body: until the client closes
            chunk = conn.recv(4096)
            if not chunk:
                break
            body += chunk
        reply = str(len(body)).encode()
        conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(reply) + reply)
