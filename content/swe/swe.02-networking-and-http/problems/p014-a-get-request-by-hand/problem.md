# A GET request by hand

Chapter section 7.2: HTTP is text on a TCP connection. Write

```python
http_get(host, port, path)    # -> (status, headers, body)
```

using only the `socket` module:

1. Connect to `(host, port)` with a 5-second timeout.
2. Send exactly this request (CRLF line ends, ASCII):

   ```text
   GET <path> HTTP/1.1
   Host: <host>:<port>
   Connection: close

   ```
3. Read until the server closes the connection (that is why we sent `Connection: close`).
4. Split the response at the first blank line. Return:
   - `status`: the status code as an `int`;
   - `headers`: a dict with **lower-case** names and stripped values;
   - `body`: **bytes** (cut to `Content-Length` if the header is there).

`path` may contain a query (`/search?q=a%20b`): send it unchanged. The test servers run on `127.0.0.1` with a free port.

## Example

```python
status, headers, body = http_get("127.0.0.1", 8080, "/hello")
status                       # 200
headers["content-type"]      # "text/plain"
body                         # b"hi"
```
