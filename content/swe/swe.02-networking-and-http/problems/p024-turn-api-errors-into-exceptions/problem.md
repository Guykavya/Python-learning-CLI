# Turn API errors into exceptions

Chapter sections 14.3 and 18.3: a good API reports errors in JSON, `{"error": {"code": "out-of-stock", "message": "Only 2 left"}}`, but a proxy in front of it may answer with an **HTML page** (`502 Bad Gateway`). A client must turn both into one kind of exception. Write

```python
class ApiError(Exception):
    def __init__(self, status, code, message): ...    # attributes: status, code, message

raise_for_api(response)     # response: an httpx.Response
```

- Status below 400: return the response unchanged.
- Status 400 or more: raise `ApiError(status, code, message)`.
- If the body is JSON with `{"error": {"code": ..., "message": ...}}`, use them (a missing one falls back as below).
- If `error` is a string (`{"error": "nope"}`) use it as the message; if there is a `detail` string (`{"detail": "..."}`) use it as the message.
- Otherwise (HTML, empty body, garbage) use the **fallback**: the `code` is derived from the status: `400 bad-request`, `401 unauthorized`, `403 forbidden`, `404 not-found`, `409 conflict`, `422 unprocessable`, `429 too-many-requests`, `500 internal-error`, `502 bad-gateway`, `503 service-unavailable`, `504 gateway-timeout`, any other status `http-<status>`; the `message` is the standard reason phrase (`Bad Gateway`; for an unknown status `HTTP <status>`).
- `str(error)` is `"<status> <code>: <message>"`.

## Example

```python
raise_for_api(httpx.Response(200, json={}))            # the response itself
raise_for_api(httpx.Response(404, json={"error": {"code": "no-book", "message": "No book 7"}}))
# ApiError: 404 no-book: No book 7
raise_for_api(httpx.Response(502, text="<html>Bad Gateway</html>"))
# ApiError: 502 bad-gateway: Bad Gateway
```
