## Hint 1

If you take off the `scheme://` from the front and the `#fragment` from the end first, what is left? Which piece should you remove next?

## Hint 2

Order: `partition("://")`, then `partition("#")`, then `partition("?")`, then `partition("/")` (host and port on the left, path on the right), then `partition(":")` on the host part. A missing part is `""`, and `"" or "(none)"` gives the default.

## Hint 3

```
scheme, sep, rest = input().strip().partition("://")
rest, sep, fragment = rest.partition("#")
rest, sep, query = rest.partition("?")
hostport, sep, path = rest.partition("/")
host, sep, port = hostport.partition(":")
print("Scheme:", scheme.lower())
print("Host:", host.lower())
print("Port:", port or "(default)")
print("Path:", "/" + path)
print("Query:", query or "(none)")
print("Fragment:", fragment or "(none)")
```
