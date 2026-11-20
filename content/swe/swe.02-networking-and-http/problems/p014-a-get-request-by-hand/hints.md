## Hint 1

A request is just the string in the statement, encoded as bytes. Which socket call sends all of it? What marks the end of the response when you asked the server to close?

## Hint 2

Loop on `recv` until it returns `b""`. Then `partition(b"\r\n\r\n")` cuts the head from the body. The first line of the head is the status line: `HTTP/1.1 200 OK`.

## Hint 3

```text
sock = create_connection((host, port), timeout=5)
sock.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n".encode())
data = read until recv() == b""
head, _, body = data.partition(b"\r\n\r\n")
status = int(first line .split(" ")[1])
headers = lower-cased names from the other lines
```
