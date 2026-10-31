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
