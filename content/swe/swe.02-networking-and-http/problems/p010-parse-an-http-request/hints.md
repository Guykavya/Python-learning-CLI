## Hint 1

Where does the head end and the body begin? Which byte sequence marks it? Split there first, then parse the head line by line.

## Hint 2

`Headers` can be a list of pairs: `get` loops comparing lower-case names, `get_all` collects all matches. Why is a dictionary not enough (think: two `Set-Cookie` headers)?

## Hint 3

```text
head, sep, rest = data.partition(b"\r\n\r\n"); no sep -> BadRequest
lines = head.decode("latin-1").split("\r\n")
request line: split(" ") must give 3 parts, parts[2] starts with "HTTP/"
each other line: name, colon, value = line.partition(":"); checks; pairs.append((name, value.strip()))
HTTP/1.1 and no Host -> BadRequest
length from Content-Length (digits only, all copies equal); body = rest[:length]; too short -> BadRequest
```
