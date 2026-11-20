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
