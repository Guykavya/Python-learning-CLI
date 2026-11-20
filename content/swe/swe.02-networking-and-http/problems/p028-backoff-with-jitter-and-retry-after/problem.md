# Backoff with jitter and `Retry-After`

Chapter sections 21.3 and 21.4. Write two functions.

```python
delays(attempts, base, cap, rng)          # -> list of `attempts` waiting times
retry_after(header, now, cap=None)        # -> seconds to wait, or None
```

**`delays`**: the wait before retry number `i` (`i = 0, 1, 2, ...`) uses **full jitter**: a random number between `0` and `min(cap, base * 2**i)`. Draw it with `rng.uniform(0, ceiling)`; `rng` is a `random.Random` (or any object with `uniform`). The result has one value per attempt, in order.

**`retry_after`** reads a `Retry-After` header value:

- `None` gives `None`;
- digits only (`"30"`) give that number of seconds (an `int`);
- an HTTP date (`"Sat, 07 Nov 2026 10:00:30 GMT"`) gives the seconds from `now` (a timezone-aware `datetime`) to that date, **never negative** (a date in the past gives `0`);
- anything else (`"soon"`, `""`, `"-5"`) gives `None`;
- if `cap` is not `None`, the result is at most `cap` (never trust a server that says "wait one day").

## Example

```python
import random
delays(4, 0.5, 8.0, random.Random(1))     # four numbers, in [0, 0.5], [0, 1], [0, 2], [0, 4]
retry_after("30", now)                      # 30
retry_after("Sat, 07 Nov 2026 10:00:30 GMT", now)   # 30.0 when now is 10:00:00
retry_after("86400", now, cap=60)           # 60
```
