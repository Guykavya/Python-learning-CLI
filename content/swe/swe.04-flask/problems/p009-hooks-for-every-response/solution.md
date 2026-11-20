## Approach

One `before_request` that decides the id, one `after_request` that stamps the response.

```python
import re
import uuid

from flask import Flask, g, request

VALID_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(test_config or {})

    @app.before_request
    def set_request_id():
        incoming = request.headers.get("X-Request-ID", "")
        g.request_id = incoming if VALID_ID.fullmatch(incoming) else uuid.uuid4().hex

    @app.after_request
    def add_headers(response):
        response.headers["X-Request-ID"] = g.get("request_id", "")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.get("/whoami")
    def whoami():
        return g.request_id

    return app
```

Example: for `GET /missing`, no view matches, but the request still goes through the lifecycle of section 5.6: `before_request` runs, the 404 error response is made, `after_request` runs. That is why a hook is the right place for headers that every response needs.

The id is validated because it is copied into the response and into logs: an attacker could send a very long value, or characters that confuse your log format. Unknown input is replaced, not repaired.

## Complexity

`O(1)` per request.

## Another way

Frameworks and proxies often set `X-Request-ID` themselves; the app then reuses it (as here) so one id follows a request through the proxy, the app and the logs. Security headers are also often added by the web server (nginx), but setting them in the app keeps them in the tests.

## Not covered

A real service would put the id in every log line (a logging filter that reads `g`) and pass it to the services it calls.
