# Build a response

Write `build_response(status, body="", content_type="text/plain; charset=utf-8")` returning the **bytes** of an HTTP/1.1 response (chapter sections 8.2 and 11.2):

```text
HTTP/1.1 200 OK\r\n
Content-Type: text/plain; charset=utf-8\r\n
Content-Length: 2\r\n
\r\n
hi
```

- The status line is `HTTP/1.1`, the code and the **reason phrase** from `http.HTTPStatus` (`200 OK`, `404 Not Found`, `418 I'm a Teapot`). For a code the module does not know use `Unknown`.
- `body` is `str` (encode it as UTF-8) or `bytes` (use as is).
- `Content-Length` is the number of **bytes** of the encoded body, not the number of characters.
- Header order: `Content-Type`, then `Content-Length`. Every line ends with `\r\n`; a blank line `\r\n` ends the headers; then the body.
- For `204`, `304` and `1xx` the response has **no body, no `Content-Type` and no `Content-Length`**: only the status line and the blank line. A non-empty body for them raises `ValueError`.

## Example

```python
build_response(200, "hi")
# b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 2\r\n\r\nhi'
build_response(404, "é")       # Content-Length: 2   (é is two bytes in UTF-8)
```
