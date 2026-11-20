## Hint 1

What do the two environ keys `PATH_INFO` and `QUERY_STRING` hold for the request `GET /hello?name=Asha`? And which standard-library function turns `"name=Asha"` into a dictionary?

## Hint 2

`parse_qs("name=Asha")` returns `{"name": ["Asha"]}`: every value is a **list**, because a key may repeat. Take the first item, with a default when the key is missing.

## Hint 3

```text
if PATH_INFO == "/hello":
    name = first value of parse_qs(QUERY_STRING)["name"], default "world"
    status, text = "200 OK", "Hello, " + name
else:
    status, text = "404 Not Found", "Not Found"
body = text.encode("utf-8")
start_response(status, [Content-Type, Content-Length = len(body)])
return [body]
```
