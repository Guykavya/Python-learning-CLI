## Approach

Split the job in two. `default_get` is a thin shell around urllib and the only code that can open a
socket. `fetch_title` holds the logic and receives `http_get` as a parameter, so tests pass a three-line
fake. `default_get` itself is tested by replacing `urllib.request.urlopen` (the edge) with a fake
response, and a guard proves that no test ever reaches a real socket.

## Code

```python
import json
import urllib.error
import urllib.request


def default_get(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, ""


def fetch_title(url, http_get=None):
    if http_get is None:
        http_get = default_get
    status, body = http_get(url)
    if status == 404:
        return None
    if status != 200:
        raise RuntimeError(f"HTTP {status} for {url}")
    try:
        data = json.loads(body)
    except ValueError:
        raise ValueError(f"bad JSON from {url}") from None
    return data["title"]
```

## Complexity

O(size of the body) for parsing; one request per call.

## Another way

Use `unittest.mock.patch("solution.default_get")` instead of the `http_get` parameter. It works, but the
parameter makes the dependency visible in the signature and needs no patching.
