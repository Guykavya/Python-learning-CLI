## Hint 1

`ipaddress.ip_address(text)` returns an address object or raises `ValueError`. What does the object offer? Look for attributes starting with `is_`.

## Hint 2

The flags overlap (`127.0.0.1.is_private` is `True`), so the order of your checks decides the answer. Put the most specific category first.

## Hint 3

```text
try: ip = ipaddress.ip_address(addr)
except (ValueError, TypeError)? -> "invalid"   (ip_address(None) raises ValueError)
if ip.is_loopback: "loopback"
elif ip.is_link_local: "link-local"
elif ip.is_private: "private"
elif ip.is_global and not ip.is_multicast: "global"
else: "other"
```
