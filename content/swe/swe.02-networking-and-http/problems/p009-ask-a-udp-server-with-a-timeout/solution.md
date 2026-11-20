## Approach

```python
import socket
import time


def udp_ask(port, text, timeout, tries):
    server = ("127.0.0.1", port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        for _ in range(tries):
            sock.sendto(text.encode("utf-8"), server)
            deadline = time.monotonic() + timeout
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                sock.settimeout(remaining)
                try:
                    data, addr = sock.recvfrom(65535)
                except socket.timeout:
                    break
                if addr == server:
                    return data.decode("utf-8")
        return None
    finally:
        sock.close()
```

The timeout is a **deadline for this attempt**: a stranger's datagram makes `recvfrom` return early, so we compute the remaining time again instead of waiting a fresh `timeout` (otherwise an attacker could keep us waiting for ever by sending junk). `time.monotonic()` is the right clock: it never jumps backwards.

Example: with the first datagram lost, `recvfrom` times out after 0.5 s; the loop sends again; the second datagram is answered and `"pong"` is returned.

## Complexity

At most `tries * timeout` seconds of waiting.

## Another way

Real protocols add an id to each request and check it in the reply (DNS does), so that a late reply to the first try is not mistaken for the answer to the second. Checking the source address is the minimum.

## Why it matters

UDP is used for DNS, games and streaming. "Send, wait, resend, give up" is the pattern in every UDP client.
