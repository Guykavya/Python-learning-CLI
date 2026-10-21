## Approach

Peel off one part at a time, always from the outside, so that later separators cannot be confused with earlier ones. For example, a query may contain `/` or `:`, so the query must be removed **before** looking for the path or the port.

| Step | Call | Leaves |
|---|---|---|
| 1 | `partition("://")` | scheme, then the rest |
| 2 | `partition("#")` | fragment removed |
| 3 | `partition("?")` | query removed |
| 4 | `partition("/")` | host and port, then the path (without its first `/`) |
| 5 | `partition(":")` | host, then port |

## Code

```python
scheme, sep, rest = input().strip().partition("://")
rest, sep, fragment = rest.partition("#")
rest, sep, query = rest.partition("?")
hostport, sep, path = rest.partition("/")
host, sep, port = hostport.partition(":")
print(f"Scheme: {scheme.lower()}")
print(f"Host: {host.lower()}")
print(f"Port: {port or '(default)'}")
print(f"Path: /{path}")
print(f"Query: {query or '(none)'}")
print(f"Fragment: {fragment or '(none)'}")
```

## Another way

In real code use `urllib.parse.urlsplit(url)`, which handles many more cases (user names, IPv6 hosts, percent-escapes). Writing it by hand once shows you how such parsers think.
