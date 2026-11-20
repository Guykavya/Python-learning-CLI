## Approach

```python
import math
from datetime import timezone
from email.utils import parsedate_to_datetime


def delays(attempts, base, cap, rng):
    return [rng.uniform(0, min(cap, base * 2 ** i)) for i in range(attempts)]


def retry_after(header, now, cap=None):
    if header is None:
        return None
    value = header.strip()
    if value.isascii() and value.isdigit():
        seconds = int(value)
    else:
        try:
            when = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        seconds = max(0, (when - now).total_seconds())
    return min(seconds, cap) if cap is not None else seconds
```

`min(cap, base * 2**i)` doubles the ceiling each time but never above `cap`: with `base=0.5`, `cap=8` the ceilings are 0.5, 1, 2, 4, 8, 8, ... **Full jitter** means the actual wait is anywhere from 0 up to the ceiling, which spreads a crowd of clients over time instead of sending them back in one wave. `retry_after` prefers the server's word: it knows better than your formula. `isdigit()` accepts only non-negative integers, so `"-5"` falls through to the date parser and fails there: `None`.

Example: `retry_after("86400", now, cap=60)` is `min(86400, 60) = 60`.

## Complexity

`O(attempts)` and `O(1)`.

## Another way

"Equal jitter" waits `ceiling/2 + random(0, ceiling/2)`: fewer very short waits, a bit less spreading. Full jitter is the simplest and usually the best.

## Why it matters

Fixed-delay retries make a struggling server worse (a retry storm). Jittered backoff and obeying `Retry-After` are what polite clients do.
