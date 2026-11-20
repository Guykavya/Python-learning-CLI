## Hint 1

Which socket type is UDP (`SOCK_DGRAM`)? Which two calls send and receive datagrams? How do you make a receive give up after some time?

## Hint 2

`recvfrom` returns `(data, address)`. Compare the address with the server's `("127.0.0.1", port)`. If it differs, do not return: keep waiting, but only for the **rest** of the timeout, not a fresh one.

## Hint 3

```text
sock = UDP socket
for attempt in range(tries):
    sock.sendto(data, ("127.0.0.1", port))
    deadline = now + timeout
    while True:
        remaining = deadline - now; if remaining <= 0: break
        sock.settimeout(remaining)
        try: reply, addr = sock.recvfrom(65535)
        except socket.timeout: break
        if addr == ("127.0.0.1", port): return reply.decode()
return None   (close the socket in a finally)
```
