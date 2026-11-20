import math

from fastapi import HTTPException


class TokenBucket:
    def __init__(self, capacity, rate, clock):
        self.capacity = capacity
        self.rate = rate
        self.clock = clock
        # TODO: start full, remember the time of the last refill

    def take(self):
        """Return (True, 0) if a token was used, else (False, seconds_to_wait)."""
        raise NotImplementedError("write take()")


def rate_limit(bucket):
    """Return a FastAPI dependency that raises 429 with a Retry-After header when the bucket is empty."""
    raise NotImplementedError("write rate_limit()")
