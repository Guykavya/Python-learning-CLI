## Hint 1

Make a loop over `attempt` in `range(retries + 1)`. Inside, put the request in a `try`. For each
way it can end, decide one of three things: **return**, **raise now**, or **sleep and loop
again**. Which outcome is which for: 200, 404, 503 on attempt 0, 503 on the last attempt,
`ConnectError`?

## Hint 2

`raise_for_status()` turns 4xx/5xx into `httpx.HTTPStatusError`; the status is in
`error.response.status_code`. Connection problems are `httpx.TransportError`. A bare `raise`
inside `except` re-raises the error you are handling.

```
for attempt in range(retries + 1):
    last = (attempt == retries)
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response
    except HTTPStatusError as e:
        if status < 500 or last: raise
    except TransportError:
        if last: raise
    await sleep(base_delay * 2 ** attempt)
```
