## Hint 1

Loop `for attempt in range(1, max_attempts + 1)`. Each attempt ends in exactly one of four
ways: **return** the JSON, **raise now** (a permanent 4xx), **raise because it was the last
attempt**, or **wait and loop again**. For each of these, which one is it: 200, 404, 429 on
attempt 1, 503 on attempt 4, `ConnectError` on attempt 2, `ValueError`?

## Hint 2

Keep the decision ("retry or not") in the `except` blocks and the waiting after them, so a
`return` or `raise` skips the sleep automatically. Only the HTTP error has a response with
headers; a transport error has none.

```
for attempt in 1..max_attempts:
    response = None
    try:
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()
    except HTTPStatusError as e:
        status = e.response.status_code
        if status != 429 and status < 500: raise       # permanent
        if attempt == max_attempts: raise
    except TransportError:
        if attempt == max_attempts: raise
    header = response.headers.get("Retry-After", "") if response else ""
    if header is all digits: delay = min(int(header), max_delay)
    else: backoff = min(max_delay, base_delay * 2**(attempt-1)); delay = backoff/2 + rand()*backoff/2
    logger.warning(...); sleep(delay)
```
