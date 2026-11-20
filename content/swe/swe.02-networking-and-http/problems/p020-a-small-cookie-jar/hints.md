## Hint 1

What identifies a cookie? Three things: host, path and name. A dictionary keyed by that triple gives you "same name replaces", and its insertion order gives "creation order".

## Hint 2

Split the header at `;`. The first piece is `name=value` (`partition("=")`, so that `=` inside the value survives). The other pieces are attributes: lower-case the key and look at `path`, `secure`, `httponly`, `max-age`.

## Hint 3

```text
header_for: keep cookies with the same host, not expired, (https or not secure), path_match
path_match(cp, rp): cp == rp, or rp starts with cp and (cp ends with "/" or the next character of rp is "/")
sort by -len(path) (sorting is stable: equal paths keep creation order)
```
