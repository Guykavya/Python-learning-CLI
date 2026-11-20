## Hint 1

Write one private function that does *one request with retries*, for a given `repeatable` flag, and let `get_json` and `post_json` call it. For a `GET` the flag is true. For a `POST` it is true only with a key.

## Hint 2

The loop `for attempt in range(attempts)`: inside, try the request. A transport error is retryable if it is a connect error (never sent) or the request is repeatable. A bad status is retryable if it is in the set **and** the request is repeatable. Raise on non-retryable failures and on the last attempt; otherwise sleep and go on.

## Hint 3

```text
for attempt in range(attempts):
    last = attempt == attempts - 1
    try: response = client.request(...)
    except httpx.TransportError as exc: retryable = connect error or (repeatable and read-type error); if not retryable or last: raise RequestFailed
    else: status < 400 -> return;  not in RETRY_STATUSES or not repeatable or last -> raise RequestFailed(status)
    sleep(Retry-After (<= 30) if present else rng.uniform(0, min(8, 0.5 * 2**attempt)))
```
