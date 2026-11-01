import asyncio
import time
from collections import deque


class RateLimiter:
    """At most `rate` starts in any `per` seconds (sliding window), first come first served."""

    def __init__(self, rate, per, clock=time.monotonic, sleep=asyncio.sleep):
        self.rate = rate
        self.per = per
        self.clock = clock
        self.sleep = sleep
        self.starts = deque()       # times of the starts still inside the window

    async def __aenter__(self):
        raise NotImplementedError("drop expired starts; wait while the window is full; record now")

    async def __aexit__(self, exc_type, exc, tb):
        return False
