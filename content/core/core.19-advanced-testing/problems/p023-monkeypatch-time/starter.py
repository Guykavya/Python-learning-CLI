import time


def now():
    return time.monotonic()


class RateLimiter:
    def __init__(self, limit, per_seconds):
        self.limit = limit

    def allow(self):
        return True
