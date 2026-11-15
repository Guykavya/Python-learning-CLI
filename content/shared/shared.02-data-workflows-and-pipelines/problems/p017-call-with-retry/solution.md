## Approach

Three questions decide every retry policy.

1. **Is the failure temporary?** 429 (rate limit), 5xx (server trouble) and transport errors
   (the network) usually are. Other 4xx mean *our* request is wrong (bad parameter, no
   permission, unknown id): retrying only adds load and delays the real error. Anything that
   is not an HTTP or transport error is a bug and must surface immediately.
2. **How long to wait?** If the server says (`Retry-After: 7`), obey it exactly; it knows its
   own rate limit. Otherwise back off exponentially (1, 2, 4, 8 ...) so a struggling server gets
   more breathing room each time, capped at `max_delay` so one call never sleeps for minutes.
   Jitter (a random part) spreads clients out: if 500 pipeline workers fail at the same
   second, exact backoff makes them all retry at the same second again.
3. **When to stop?** After `max_attempts` requests, re-raise the last real error so the caller
   sees the status code and traceback. Never sleep after the last attempt.

`sleep` and `rand` are parameters (dependency injection): production uses the real ones, tests
pass fakes and check the exact delays without waiting.

## Code

```python
import logging
import random
import time

import httpx

logger = logging.getLogger("pipeline")


def retry_after_seconds(response):
    if response is None:
        return None
    value = response.headers.get("Retry-After", "").strip()
    return int(value) if value.isdigit() else None


def call_with_retry(client, path, params=None, *, max_attempts=4, base_delay=1.0,
                    max_delay=30.0, sleep=time.sleep, rand=random.random):
    for attempt in range(1, max_attempts + 1):
        response = None
        try:
            response = client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            if status != 429 and status < 500:
                raise
            if attempt == max_attempts:
                raise
            reason = str(status)
        except httpx.TransportError as error:
            if attempt == max_attempts:
                raise
            reason = type(error).__name__

        wait = retry_after_seconds(response)
        if wait is not None:
            delay = float(min(wait, max_delay))
        else:
            backoff = min(max_delay, base_delay * 2 ** (attempt - 1))
            delay = backoff / 2 + rand() * backoff / 2
        logger.warning("attempt %d failed (%s), retrying in %.2fs", attempt, reason, delay)
        sleep(delay)
```

## Complexity

At most `max_attempts` requests. The worst-case total wait without `Retry-After` is the sum
of the capped backoffs: with the defaults 1 + 2 + 4 = 7 seconds over 3 retries.

## Another way

Check the status yourself instead of using exceptions:
`if response.is_success: return response.json()`, then decide on `response.status_code` and call
`response.raise_for_status()` when you give up. Both are fine; the exception version keeps
"what counts as an error" in one place (httpx).

`Retry-After` may also be an HTTP date (`Wed, 21 Oct 2026 07:28:00 GMT`). A fuller helper parses
it with `email.utils.parsedate_to_datetime` and waits until then. Libraries such as `tenacity`
wrap this pattern in a decorator (httpx's own `HTTPTransport(retries=...)` only retries failed
connections, not 429 or 5xx). The loop above is all they do underneath, and knowing it lets you
choose the policy instead of accepting a default.
