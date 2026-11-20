## Approach

```python
import math
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FIX = {400, 404, 405, 409, 410, 415, 422}
RETRY = {408, 500, 502, 504}
REDIRECTS = {301, 302, 303, 307, 308}


def _retry_after(value, now):
    value = value.strip()
    if value.isascii() and value.isdigit():
        return int(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0, math.ceil((when - now).total_seconds()))


def client_action(status, headers, now=None):
    headers = {k.lower(): v for k, v in headers.items()}
    if now is None:
        now = datetime.now(timezone.utc)
    if 200 <= status < 300 or status == 304:
        return "use"
    if status in REDIRECTS:
        location = headers.get("location")
        return f"follow:{location}" if location else "give-up"
    if status in (429, 503):
        seconds = _retry_after(headers["retry-after"], now) if "retry-after" in headers else None
        return f"wait:{seconds}" if seconds is not None else "retry"
    if status in RETRY:
        return "retry"
    if status == 401:
        return "log-in"
    if status in FIX:
        return "fix-request"
    return "give-up"
```

Lower-casing the header names once makes every later lookup simple. `Retry-After` is handled in one helper: digits mean seconds, otherwise a date is parsed (an HTTP date always ends in `GMT`, so it is timezone-aware; a naive one is treated as UTC). `math.ceil` rounds up so that the client never wakes **before** the server is ready. A `429` with no usable `Retry-After` falls back to `"retry"` (the caller then uses its own backoff).

Example: `client_action(503, {"Retry-After": "Sat, 07 Nov 2026 10:00:30 GMT"}, now=10:00:00)` is `"wait:30"`.

## Complexity

`O(1)`.

## Another way

A dictionary from status to action handles the simple codes; the `Retry-After` and `Location` cases need code anyway.

## Why it matters

A client that treats every error alike either hammers a server that asked to be left alone, or retries a `404` forever. The family of the status tells it what to do (chapter section 10.4).
