## Approach

```python
import ipaddress


def client_ip(remote_addr, x_forwarded_for=None, trusted_proxies=1):
    if trusted_proxies <= 0 or not x_forwarded_for:
        return remote_addr                                         # no trusted proxy: the header is just user input
    chain = [part.strip() for part in x_forwarded_for.split(",")] + [remote_addr]
    if len(chain) < trusted_proxies + 1:
        return remote_addr                                         # the request did not pass through all our proxies
    candidate = chain[-(trusted_proxies + 1)]
    try:
        ipaddress.ip_address(candidate)
    except ValueError:
        return remote_addr                                         # garbage such as "unknown"
    return candidate
```

Why the right side: a proxy appends, never inserts at the left. So the right-most entries come from machines you run. Everything left of them was already in the header when the request reached your first proxy, so the client (or an earlier machine you do not control) wrote it. With one proxy the chain `[1.2.3.4, 203.0.113.7, 10.0.0.1]` has the attacker's lie at index 0, the real client at `-2`, and our proxy at `-1`. An attacker who sends a different random left-hand value on every request changes nothing: the answer stays `203.0.113.7`, so they cannot get a fresh rate-limit bucket by rotating the header (the attack of the chapter's "Try it: the spoofed header").

The fall-backs all end in `remote_addr`: when in doubt, use the address the operating system saw on the connection, which cannot be forged by header tricks.

## Complexity

O(n) time and memory in the length of the header; a real server also caps the header size.

## Another way

Walk from the right and skip addresses that belong to **known proxy networks** (a list of CIDRs), stopping at the first address that is not one of yours. This needs no proxy count, so it still works if a proxy is added later, but it needs a correct list of ranges. Uvicorn's `--forwarded-allow-ips` and nginx's `real_ip_recursive` work this way.
