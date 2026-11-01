# Retry with exponential backoff

Networks fail in two different ways:

- **Temporary** failures: the server answers 500, 502, 503 or 504 (it is overloaded or
  restarting), or the connection itself breaks (`httpx.TransportError`, for example
  `httpx.ConnectError`). Trying again a little later often works.
- **Permanent** failures: 400, 401, 403, 404 and the other 4xx codes. *You* asked for something
  wrong. Asking again gives the same answer, so retrying only wastes time.

Write

```python
async def get_with_retry(client, url, retries=3, base_delay=0.1, sleep=asyncio.sleep):
```

- Send `GET url` with `client`. On a 2xx/3xx answer, return the `httpx.Response`.
- On a 4xx answer, raise `httpx.HTTPStatusError` at once (no retry).
- On a 5xx answer or an `httpx.TransportError`, wait and try again, up to `retries` **extra**
  attempts (so at most `retries + 1` requests).
- Wait `base_delay * 2**k` before retry number `k + 1`: `0.1`, `0.2`, `0.4`, ... This is
  *exponential backoff*: each failure gives the server more time to recover.
- Do the waiting with `await sleep(delay)`, using the `sleep` **parameter**, never
  `asyncio.sleep` directly. The tests pass a fake `sleep` that only records the delays, so they
  run instantly.
- If the last attempt still fails, raise its error (`HTTPStatusError` for 5xx, or the transport
  error itself). Do not sleep after the last attempt.

**Example**

```python
# server answers 503, 503, then 200
response = await get_with_retry(client, "https://api.test/data", sleep=fake_sleep)
response.status_code       # 200
fake_sleep.delays          # [0.1, 0.2]

# server always answers 404
await get_with_retry(client, "https://api.test/nope", sleep=fake_sleep)
# httpx.HTTPStatusError (1 request, no sleeps)
```
