## Hint 1

What can go wrong when you call `response.json()` on an HTML page? Which exception type, and what do you do with it?

## Hint 2

Start from the fallback values (code from the status, message from the reason phrase). Then overwrite them **only if** the body gives better information.

## Hint 3

```text
code = CODES.get(status, f"http-{status}"); message = HTTPStatus(status).phrase (unknown -> "HTTP <status>")
try: data = response.json()  except ValueError: data = None
if data is a dict:
    error = data.get("error")
    dict -> code/message from it (fall back for missing parts); str -> message; elif data["detail"] is str -> message
raise ApiError(status, code, message)
```
