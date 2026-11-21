import time


class CircuitOpen(Exception):
    """Raised without calling the dependency at all."""


class CircuitBreaker:
    """closed -> (too many failures) -> open -> (after reset_after) -> half-open -> closed or open."""

    def __init__(self, failure_threshold=3, reset_after=10.0, clock=time.monotonic):
        self.failure_threshold = failure_threshold
        self.reset_after = reset_after
        self.clock = clock
        self.state = "closed"
        self.failures = 0
        self.opened_at = None

    def call(self, fn):
        if self.state == "open":
            if self.clock() - self.opened_at < self.reset_after:
                raise CircuitOpen("dependency is failing; not calling it")
            self.state = "half-open"                 # let one probe call through
        try:
            result = fn()
        except Exception:
            self._failure()
            raise
        self.failures = 0
        self.state = "closed"
        return result

    def _failure(self):
        self.failures += 1
        if self.state == "half-open" or self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = self.clock()


POPULAR = ("Python tips", "Testing basics", "Docker intro")


def recommendations(user, primary, cache, breaker, timeout=0.5, popular=POPULAR):
    try:
        items = breaker.call(lambda: primary(user, timeout=timeout))
    except Exception:                                   # a timeout, an error, or CircuitOpen: the page must still load
        if user in cache:
            return {"items": list(cache[user]), "stale": True, "source": "cache"}
        return {"items": list(popular), "stale": True, "source": "popular"}
    cache[user] = list(items)
    return {"items": list(items), "stale": False, "source": "primary"}
