import asyncio
import time
from collections import deque


class RateLimiter:
    """At most `rate` starts in any `per` seconds (sliding window), first come first served."""

    def __init__(self, rate, per, clock=time.monotonic, sleep=asyncio.sleep):
        if rate < 1:
            raise ValueError("rate must be at least 1")
        if per <= 0:
            raise ValueError("per must be positive")
        self.rate = rate
        self.per = per
        self.clock = clock
        self.sleep = sleep
        self.starts = deque()          # times of the starts still inside the window
        self._lock = asyncio.Lock()    # FIFO: only the first waiter checks and sleeps

    async def __aenter__(self):
        async with self._lock:
            while True:
                now = self.clock()
                while self.starts and self.starts[0] + self.per <= now:
                    self.starts.popleft()          # expired: older than `per`
                if len(self.starts) < self.rate:
                    self.starts.append(now)
                    return self
                await self.sleep(self.starts[0] + self.per - now)

    async def __aexit__(self, exc_type, exc, tb):
        return False                   # never swallow the body's exception
