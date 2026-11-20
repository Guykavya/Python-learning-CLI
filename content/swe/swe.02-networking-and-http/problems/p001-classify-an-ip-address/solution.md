## Approach

```python
import ipaddress


def classify(addr):
    if not isinstance(addr, str):
        return "invalid"
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return "invalid"
    if ip.is_loopback:
        return "loopback"
    if ip.is_link_local:
        return "link-local"
    if ip.is_private:
        return "private"
    if ip.is_global and not ip.is_multicast:
        return "global"
    return "other"
```

`ip_address` accepts IPv4 and IPv6 text and raises `ValueError` for bad text. It also accepts **integers** (`ip_address(12)` is `0.0.0.12`), so we reject anything that is not a `str` first. The flags overlap: `127.0.0.1` is loopback **and** private; `169.254.1.1` is link-local **and** private. Checking from the most specific category to the most general gives one clear answer.

Example: `"fe80::1"` is IPv6 link-local: `is_loopback` is false, `is_link_local` is true: `"link-local"`.

## Complexity

`O(1)`.

## Another way

Check the ranges by hand with `ipaddress.ip_network("10.0.0.0/8")` and `ip in network`. The built-in flags already know all the ranges of the RFCs, so prefer them.

## Why it matters

A server that fetches a user-supplied URL must refuse loopback and private targets, or an attacker can make it call your internal services (SSRF). This function is the core of such a check.
