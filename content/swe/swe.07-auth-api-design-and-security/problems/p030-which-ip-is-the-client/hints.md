## Hint 1

Who writes each part of the header: the client, or your proxy? Which side of the list can an attacker never touch? Write the chain for `remote_addr="10.0.0.1"` and header `"9.9.9.9, 203.0.113.7"` on paper and mark which entries your proxy wrote.

## Hint 2

Add `remote_addr` to the end of the list. With one trusted proxy, which index counted from the right is the client (`-1` is the proxy itself)? How does that index change with two proxies? What if the list has fewer items than that index needs?

## Hint 3

```text
if trusted_proxies <= 0 or not header: return remote_addr
chain = [part.strip() for part in header.split(",")] + [remote_addr]
if len(chain) < trusted_proxies + 1: return remote_addr
candidate = chain[-(trusted_proxies + 1)]
try ipaddress.ip_address(candidate) except ValueError: return remote_addr
return candidate
```
