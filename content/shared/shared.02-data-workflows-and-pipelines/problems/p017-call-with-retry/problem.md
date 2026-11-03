# call_with_retry: backoff, jitter and Retry-After

Every extract step of a pipeline calls an API, and APIs fail now and then. Write the one
helper that every request of your pipeline goes through:

```python
def call_with_retry(client, path, params=None, *, max_attempts=4, base_delay=1.0,
                    max_delay=30.0, sleep=time.sleep, rand=random.random):
```

It sends `client.get(path, params=params)` and returns the decoded JSON (`response.json()`)
of the first successful response.

**Which failures to retry**

| Failure | Retry? |
|---|---|
| status **429** (Too Many Requests) | yes |
| status **500 or higher** | yes |
| `httpx.TransportError` (connect errors, timeouts, broken connections) | yes |
| any other 4xx (400, 401, 403, 404, 409, ...) | **no**: raise `httpx.HTTPStatusError` at once |
| any other exception (a bug such as `ValueError`) | **no**: let it propagate |

`response.raise_for_status()` raises `HTTPStatusError` for 4xx and 5xx; the status is in
`error.response.status_code`.

**How long to wait before retry number `k`** (`k = 1` for the first retry):

1. If the failed response has a `Retry-After` header that is a whole number of seconds
   (for example `"7"`), wait exactly `min(that number, max_delay)` seconds. No jitter.
   Any other value (for example an HTTP date) is ignored: use rule 2.
2. Otherwise use exponential backoff with "equal jitter":
   `backoff = min(max_delay, base_delay * 2 ** (k - 1))`, then
   `delay = backoff / 2 + rand() * backoff / 2` (somewhere between half and all of `backoff`).

Wait by calling the `sleep` **parameter** (`sleep(delay)`), never `time.sleep` directly, and
call `rand()` for the jitter, never `random.random` directly. The tests pass fakes, so they
run instantly and know exactly which delays you chose.

**Giving up.** Make at most `max_attempts` requests in total. If the last one fails, raise
its error (the `HTTPStatusError` of the last response, or the last transport error). Do not
sleep after the last attempt.

**Logging.** Before each sleep, log one `WARNING` on the logger named `"pipeline"`, for
example `attempt 1 failed (503), retrying in 1.00s`. Do not log on success.

**Example**

```python
# the server answers 503, 503, then 200 with {"data": []}
call_with_retry(client, "/v1/orders", {"page": 1}, sleep=fake_sleep, rand=lambda: 1.0)
# {"data": []}       fake_sleep was called with 1.0, then 2.0

# the server answers 429 with "Retry-After: 7", then 200
# -> sleep(7.0) once (exact, no jitter)

# the server answers 404
# -> httpx.HTTPStatusError after one request, no sleep
```
