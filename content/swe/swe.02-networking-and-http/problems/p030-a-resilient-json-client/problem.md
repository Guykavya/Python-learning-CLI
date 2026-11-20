# A resilient JSON client

Chapter section 22 builds a client that survives a flaky network. Write two functions and one exception:

```python
class RequestFailed(Exception):      # attributes: .status (None if no response), .attempts
    def __init__(self, message, status=None, attempts=1): ...

get_json(client, url, attempts=4, sleep=time.sleep, rng=random)
post_json(client, url, payload, idempotency_key=None, attempts=4, sleep=time.sleep, rng=random)
```

`client` is an `httpx.Client` (the tests use a mock transport). `sleep(seconds)` and `rng` (an object with `uniform(a, b)`) are **parameters**, so tests do not wait and can control the randomness. Both functions return the decoded JSON of a successful (status below 400) response.

**What is retried** (at most `attempts` requests in all):

| Failure | `GET` | `POST` without a key | `POST` with `idempotency_key` |
|---|---|---|---|
| `httpx.ConnectError` / `ConnectTimeout` (request never reached the server) | retry | retry | retry |
| `httpx.ReadTimeout`, `ReadError`, `RemoteProtocolError` (it may have been processed) | retry | **fail at once** | retry |
| status `429`, `502`, `503`, `504` | retry | **fail at once** | retry |
| any other status `>= 400` (`400`, `401`, `404`, `500`, ...) | fail at once | fail at once | fail at once |

**Waiting** between attempts (never after the last one): if the failed response has `Retry-After` with a whole number of seconds, wait that long (at most **30**); otherwise wait `rng.uniform(0, min(8.0, 0.5 * 2**k))` where `k = 0` for the wait after the first failure, `1` after the second, and so on. Call `sleep(wait)` with that number.

**Failing:** raise `RequestFailed` with `.status` (the last status, or `None` for a transport error) and `.attempts` (how many requests were really sent). A body that is not JSON raises `RequestFailed` too.

`post_json` sends the key in the header `Idempotency-Key`, the **same** key on every attempt, and the payload as JSON.

## Example

```python
# the server answers 503, 503, 200 {"ok": true}
get_json(client, url, sleep=waits.append, rng=TopRng())     # {"ok": True}; 3 requests; waits == [0.5, 1.0]
```
