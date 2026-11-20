# Classify an IP address

Chapter section 3.1: not every address is the same kind. Write `classify(addr)` that takes a **string** and returns one of:

| Result | Meaning |
|---|---|
| `"loopback"` | the machine itself: `127.0.0.1`, `::1` |
| `"link-local"` | auto-configured on one link: `169.254.x.x`, `fe80::/10` |
| `"private"` | private networks: `10.x`, `172.16-31.x`, `192.168.x`, `fc00::/7` |
| `"global"` | public internet addresses |
| `"other"` | valid, but none of the above (multicast such as `224.0.0.1`) |
| `"invalid"` | not an IP address at all (including `""`, `"999.1.1.1"`, `"1.2.3"`, `None`, or any non-string such as `12`) |

Use the standard library module `ipaddress`. Check in this order: loopback, link-local, private, global, other. An address can be in several categories in the module's own flags (`127.0.0.1` is also "private"; `224.0.0.1` counts as "global" for the module but is **multicast**, which this problem calls "other").

## Example

```python
classify("8.8.8.8")        # "global"
classify("192.168.1.20")   # "private"
classify("::1")            # "loopback"
classify("fe80::1")        # "link-local"
classify("999.1.1.1")      # "invalid"
```
