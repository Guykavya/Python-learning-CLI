import socket


def http_get(host, port, path):
    request = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n"
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(request.encode("ascii"))
        data = b""
        while True:
            chunk = sock.recv(4096)
            if chunk == b"":
                break
            data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")
    status = int(lines[0].split(" ")[1])
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    if "content-length" in headers:
        body = body[:int(headers["content-length"])]
    return status, headers, body
