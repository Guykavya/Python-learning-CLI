## Approach

Each attempt ends in one of three ways, and the code is a direct translation:

| Outcome | Action |
|---|---|
| 2xx / 3xx | return the response |
| 4xx | raise now (permanent) |
| 5xx or `TransportError`, attempts left | sleep `base_delay * 2**attempt`, try again |
| 5xx or `TransportError`, last attempt | raise this (the last) error |

The `except` blocks that decide to retry simply fall through to the `sleep` line at the bottom
of the loop. The `return` and the bare `raise` leave the loop, so the sleep never runs after a
success or after the final failure.

The `sleep` parameter is *dependency injection*: the function does not decide how to wait, the
caller does. Production passes nothing and gets `asyncio.sleep`; the tests pass a recorder and
run in milliseconds instead of waiting 0.7 s per test.

## Code

```python
import asyncio

import httpx


async def get_with_retry(client, url, retries=3, base_delay=0.1, sleep=asyncio.sleep):
    for attempt in range(retries + 1):
        last = attempt == retries
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as error:
            if error.response.status_code < 500 or last:
                raise
        except httpx.TransportError:
            if last:
                raise
        await sleep(base_delay * 2**attempt)
```

## Complexity

At most `retries + 1` requests. The total waiting time is
`base_delay * (2**retries - 1)` seconds in the worst case (0.7 s with the defaults).

## Another way

Real clients add **jitter**: `delay * random.uniform(0.5, 1.5)`. If 1,000 clients fail at the
same moment, exact backoff makes them all retry at the same moment too, hitting the server in
waves; jitter spreads them out. Many APIs also send a `Retry-After` header with 429 or 503;
a polite client waits that long instead of its own delay. Libraries such as `tenacity` wrap
this pattern in a decorator, but the loop above is all they do underneath.
