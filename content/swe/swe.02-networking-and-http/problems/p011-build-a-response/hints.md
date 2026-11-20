## Hint 1

`http.HTTPStatus(404).phrase` gives `"Not Found"`. What happens for a code that does not exist, and how do you handle it?

## Hint 2

Encode the body **before** you count. Build the head as text, encode it, and add the body bytes at the end: a `str` and a `bytes` cannot be joined.

## Hint 3

```text
phrase = HTTPStatus(status).phrase  (ValueError -> "Unknown")
body = body.encode("utf-8") if it is a str
if status in (204, 304) or 100 <= status < 200: only the status line + blank line (error if body)
head = status line, Content-Type, Content-Length (len(body)) joined by "\r\n" + "\r\n\r\n"
return head.encode() + body
```
