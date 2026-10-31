## Approach

`now()` is the one **seam** for time. Tests replace it with `monkeypatch.setattr(solution, "now", fake)`.
Because `now` itself reads `time.monotonic()` through the `time` module, replacing
`time.monotonic` also works. `allow` drops timestamps that are at least one window old, then compares
the rest with the limit; only an allowed call is recorded.

## Code

```python
import time


def now():
    return time.monotonic()


class RateLimiter:
    def __init__(self, limit, per_seconds):
        if limit < 1 or per_seconds <= 0:
            raise ValueError("limit must be >= 1 and per_seconds > 0")
        self.limit = limit
        self.per_seconds = per_seconds
        self.calls = []

    def allow(self):
        t = now()
        self.calls = [c for c in self.calls if t - c < self.per_seconds]
        if len(self.calls) >= self.limit:
            return False
        self.calls.append(t)
        return True
```

## Complexity

`allow` is O(limit) time and memory (at most `limit` timestamps are kept).

## Another way

Inject the clock (`RateLimiter(3, 10, clock=time.monotonic)`), as in the previous problem. Injection
needs no patching, so prefer it when you own the code.
