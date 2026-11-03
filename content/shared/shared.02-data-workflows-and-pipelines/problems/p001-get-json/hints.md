## Hint 1

There are four ways the call can end: a 4xx/5xx status, a 204, a 2xx with good JSON, and a
2xx with a body that is not JSON. Which check must come first so that an HTML 404 page is
reported as "404", not as "not JSON"? What does `response.json()` raise when the body is not
JSON? (Look at the base class of `json.JSONDecodeError`.)

## Hint 2

```
response = client.get(path, params=params)
response.raise_for_status()
if response.status_code == 204: return None
try:
    return response.json()
except ValueError as error:
    raise NotJSONError(f"{path} ... {response.text[:80]!r}") from error
```
