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
        return None
    header = first + _recv_exactly(sock, 4 - len(first))
    (n,) = struct.unpack(">I", header)
    if n > LIMIT:
        raise ValueError(f"message too large: {n} bytes")
    return _recv_exactly(sock, n).decode("utf-8")
