## Approach

Order matters. First `raise_for_status()`: a 404 or 500 is a failed call no matter what the body
looks like, and the caller (for example a retry helper later in this module) needs the
`HTTPStatusError` with its status code to decide what to do. Then handle 204, which has no body
by definition. Only then parse.

`response.json()` raises `json.JSONDecodeError` for a bad body, and `JSONDecodeError` is a
subclass of `ValueError`, so `except ValueError` catches it. We wrap it in our own
`NotJSONError` for two reasons: the caller can catch exactly this case, and the message can say
*which* call failed and *what came back*. The body is cut to 80 characters because the typical
non-JSON answer is a big HTML page from a proxy or a login screen, and you do not want that
inside every log line. `raise ... from error` keeps the original error as `__cause__`, so the
traceback still shows the exact line and column where parsing failed.

## Code

```python
import httpx


class NotJSONError(ValueError):
    """The server answered, but the body was not JSON."""


def get_json(client, path, params=None):
    response = client.get(path, params=params)
    response.raise_for_status()
    if response.status_code == 204:
        return None
    try:
        return response.json()
    except ValueError as error:
        snippet = response.text[:80]
        raise NotJSONError(
            f"{path} did not return JSON (status {response.status_code}): {snippet!r}"
        ) from error
```

## Complexity

One request. Parsing is O(n) in the size of the body.

## Another way

You can check the `Content-Type` header first:
`if not response.headers.get("content-type", "").startswith("application/json"): raise ...`.
That catches HTML pages early, but some servers send correct JSON with a wrong or missing
content type, so many pipelines only *log* a wrong content type and still try to parse.
Trying `response.json()` and catching the error is the check that never lies.
