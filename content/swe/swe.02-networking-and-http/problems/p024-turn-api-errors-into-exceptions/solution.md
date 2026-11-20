## Approach

```python
from http import HTTPStatus

CODES = {400: "bad-request", 401: "unauthorized", 403: "forbidden", 404: "not-found", 409: "conflict",
         422: "unprocessable", 429: "too-many-requests", 500: "internal-error", 502: "bad-gateway",
         503: "service-unavailable", 504: "gateway-timeout"}


class ApiError(Exception):
    def __init__(self, status, code, message):
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


def raise_for_api(response):
    status = response.status_code
    if status < 400:
        return response
    code = CODES.get(status, f"http-{status}")
    try:
        reason = HTTPStatus(status).phrase
    except ValueError:
        reason = f"HTTP {status}"
    message = reason
    try:
        data = response.json()
    except ValueError:
        data = None
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            code = error.get("code") or code
            message = error.get("message") or message
        elif isinstance(error, str):
            message = error
        elif isinstance(data.get("detail"), str):
            message = data["detail"]
    raise ApiError(status, code, message)
```

The function starts with safe defaults, so every path ends with a complete `ApiError`, whatever the server sent. `response.json()` raises `ValueError` (its `JSONDecodeError` subclass) for HTML and empty bodies; catching it is what keeps a `502` proxy page from turning into a confusing traceback. Checking the types (`isinstance(..., dict)`) protects against valid JSON of the wrong shape (a list, a number).

Example: a `502` with the body `<html>Bad Gateway</html>`: `json()` fails, so `code` stays `bad-gateway` and `message` is the phrase `Bad Gateway`.

## Complexity

`O(size of the body)`.

## Another way

`response.raise_for_status()` raises `httpx.HTTPStatusError`; wrapping it loses the server's own code and message. Reading the body gives the caller something it can act on (`out-of-stock` versus `bad-gateway`).

## Why it matters

Callers of your client should write `except ApiError as e: if e.code == "out-of-stock": ...`, not parse text. A uniform exception, even for failures that bypass the API's own error format, makes that possible.
