## Hint 1

What does the text look like when the host is an IPv6 address? Which character at the start tells you? Handle that case first.

## Hint 2

For a normal host, `rpartition(":")` splits at the **last** colon. If there is more than one colon and no brackets, you cannot know what is the host.

## Hint 3

```text
if text starts with "[": find "]"; host = inside; rest = after it; rest must be "" or ":" + port
else: count ":" ; 0 -> no port ; 1 -> host, port = split ; more -> ValueError
no port -> default for scheme (http 80, https 443, else ValueError)
port text: must be digits only (str.isdigit and isascii), 1 <= port <= 65535
host must not be empty
```
