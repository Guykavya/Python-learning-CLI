## Hint 1

Build in layers, testing each: (1) the server handles one request and closes; (2) it reads exactly `Content-Length` bytes and keeps the connection open; (3) routing and JSON errors; (4) threads and a lock; (5) the client. Chapter section 15 shows steps 1 to 3 in about 120 lines.

## Hint 2

Server: a listening socket with a short `settimeout` so that the accept loop can notice a stop flag; one thread per connection; `conn.makefile("rb")` gives you `readline()` and `read(n)`. Keep note ids safe with a `threading.Lock`. Client: copy the retry function of problem 30 and give it the paths `/notes` and `/notes/<id>`.

## Hint 3

```text
connection thread: loop { request = read request line, headers, exactly Content-Length body; None -> return
                          status, obj, extra = handle(method, path, body); send response
                          keep_alive = Connection != close and HTTP/1.1; if not keep_alive: return }
handle: /notes GET -> 200 list | POST -> parse JSON, validate, append under the lock, 201 + Location | other -> 405 Allow
        /notes/<digits> GET -> 200 or 404 | other method -> 405 Allow: GET ; anything else -> 404
client: one retry function (repeatable flag from method / key), three small methods on top
```
