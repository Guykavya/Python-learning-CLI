## Approach

```python
class LimitReq:
    def __init__(self, rate_per_s, burst=0, nodelay=False):
        if rate_per_s <= 0:
            raise ValueError(f"rate_per_s must be positive, got {rate_per_s}")
        if burst < 0:
            raise ValueError(f"burst cannot be negative, got {burst}")
        self.rate, self.burst, self.nodelay = rate_per_s, burst, nodelay
        self.excess, self.last = 0.0, None

    def allow(self, t):
        if self.last is None:
            self.last = t
            return "pass"
        if t < self.last:
            raise ValueError(f"time went backwards: {t} < {self.last}")
        new_excess = max(0.0, self.excess - self.rate * (t - self.last) + 1.0)
        if new_excess > self.burst:
            return "503"
        self.excess, self.last = new_excess, t
        return "pass" if new_excess == 0 or self.nodelay else "delayed"
```

What the parameters mean in practice (chapter 7.5): `rate` is the sustained speed; `burst` is the size of the queue that absorbs short spikes; without `nodelay`, queued requests are held back so that the real rate to the backend never exceeds `rate`; with `nodelay`, the burst goes through at once and only the refill is limited. Real Nginx answers `503` for a refused request unless `limit_req_status 429;` is set.

## Complexity

O(1) per request and O(1) memory per client (real Nginx keeps one such pair per key in the shared zone, which is why `10m` of zone holds about 160,000 addresses).

## Another way

A **fixed window counter** (swe.08 p015) is simpler but lets a client send `2 x limit` requests across a window boundary. A **token bucket** is the same idea seen from the other side: tokens refill at `rate`, a request takes one; Nginx's version counts the *excess* instead.
