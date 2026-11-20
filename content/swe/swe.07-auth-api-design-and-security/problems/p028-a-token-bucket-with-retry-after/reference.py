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
