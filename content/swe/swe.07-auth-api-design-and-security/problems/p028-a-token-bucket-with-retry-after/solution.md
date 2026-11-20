## Approach

```python
import math

from fastapi import HTTPException


class TokenBucket:
    def __init__(self, capacity, rate, clock):
        self.capacity = capacity
        self.rate = rate
        self.clock = clock
        self.tokens = float(capacity)          # starts full
        self.last = clock()

    def take(self):
        now = self.clock()
        elapsed = max(0.0, now - self.last)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)    # refill first, never above capacity
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True, 0
        return False, math.ceil((1 - self.tokens) / self.rate)                 # time until one whole token exists


def rate_limit(bucket):
    def dependency():
        allowed, wait = bucket.take()
        if not allowed:
            raise HTTPException(429, "rate limit exceeded", headers={"Retry-After": str(wait)})
    return dependency
```

The bucket stores only two numbers, so it needs the same small memory for one request per day or one million. The idle cap `min(capacity, ...)` is what makes it a *bucket*: a client that was quiet for an hour gets one full burst, not 3,600 saved-up tokens. A refusal changes only `last` and the refill, never the token count, so hammering a closed door does not push the opening time further away.

`Retry-After` is a whole number of seconds (the header also allows a date, but integers are the common choice). Rounding **up** is the safe side: a client that waits exactly that long will find a token. Rounding down would send it back too early and get a second 429.

## Complexity

O(1) time and O(1) memory per bucket. One bucket per client key means O(number of clients) memory in total (section 11.6 explains why that dictionary must live in a shared store when you run several workers).

## Another way

A *fixed window* counter is even smaller, but it lets through double the limit around a window edge (section 11.2, and the next problem). A *sliding log* is exact but stores every request time. The token bucket is the usual middle path: two numbers, and burst size and average rate are tuned separately.
