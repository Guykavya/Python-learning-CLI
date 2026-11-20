# Ask a UDP server, with a timeout

UDP has no connection and no promise of delivery (chapter section 5.2): a datagram can simply be lost. A client must **wait with a timeout and ask again**. Write

```python
udp_ask(port, text, timeout, tries)
```

It asks the UDP server on `127.0.0.1:port`:

1. send `text` (UTF-8) in one datagram;
2. wait up to `timeout` seconds **in total** for a reply from that server;
3. no reply: send again, up to `tries` datagrams in all;
4. return the reply decoded as a `str`; if nothing arrives after all `tries`, return `None`.

Only a reply that comes **from the server's address** counts: a datagram from another port (a stranger, or an attacker) is ignored and you keep waiting for the real one in the rest of the timeout. Close your socket before returning.

## Example

```python
udp_ask(9999, "ping", timeout=0.5, tries=3)    # "pong" if the server answers, None if all 3 are lost
```
