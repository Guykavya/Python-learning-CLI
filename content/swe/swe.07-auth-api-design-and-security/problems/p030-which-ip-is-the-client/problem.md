# Which IP is the client?

Chapter section 11.3 and "Try it: the spoofed header". A rate limiter needs a key per client, often the client's IP address. Behind a reverse proxy the connection comes from the **proxy**, so the real client address travels in the header `X-Forwarded-For` (XFF). The trap: the **client can send that header too** and write anything in it.

How XFF grows: each proxy **appends** the address of whoever connected to it. A client at `203.0.113.7` that sends `X-Forwarded-For: 1.2.3.4` through one proxy gives the server this header:

```text
X-Forwarded-For: 1.2.3.4, 203.0.113.7        (the left value is the attacker's lie, the right one was added by our proxy)
remote_addr:     10.0.0.1                    (the proxy's own address, from the connection)
```

So only the entries written by **your own proxies** can be trusted, and they are always on the **right**. Put the connection address at the end of the list and count from the right.

Write `client_ip(remote_addr, x_forwarded_for=None, trusted_proxies=1)` in `solution.py`:

- `remote_addr`: the address of the connection (text, IPv4 or IPv6).
- `x_forwarded_for`: the raw header value, a text like `"1.2.3.4, 203.0.113.7"`, or `None` / `""` when the header is missing.
- `trusted_proxies`: how many proxies of yours stand in front of the app (`0`, `1`, `2`, ...).

Rules:

1. Build the chain: the header entries (split on `,`, strip spaces), then `remote_addr` as the last item.
2. The client is the item `trusted_proxies + 1` places from the right: with 1 proxy it is the last header entry, with 2 proxies the second-to-last, and so on.
3. With `trusted_proxies=0` (or `<= 0`) the header is **not trusted at all**: return `remote_addr`.
4. If the header is missing or empty, return `remote_addr`.
5. If the chain is too short for that position (fewer entries than proxies, so the request did not come through your proxies as expected), return `remote_addr`.
6. If the chosen entry is not a valid IP address (`"unknown"`, `""`, text), return `remote_addr`. Use `ipaddress.ip_address` to check. Return the entry as written (stripped), not changed.

## Example

```text
client_ip("10.0.0.1", "203.0.113.7", 1)                 -> "203.0.113.7"
client_ip("10.0.0.1", "1.2.3.4, 203.0.113.7", 1)        -> "203.0.113.7"   (the left "1.2.3.4" is ignored)
client_ip("10.0.0.2", "198.51.100.5, 10.0.0.1", 2)      -> "198.51.100.5"
client_ip("203.0.113.7", "1.2.3.4", 0)                  -> "203.0.113.7"   (no proxy: remote_addr)
```

The tests import `client_ip`.
