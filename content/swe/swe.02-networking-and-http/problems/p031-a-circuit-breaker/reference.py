class CircuitOpen(Exception):
    pass


class CircuitBreaker:
    def __init__(self, threshold, cooldown, clock):
        self.threshold = threshold
        self.cooldown = cooldown
        self.clock = clock
        self._failures = 0
        self._opened_at = None

    @property
    def state(self):
        if self._opened_at is None:
            return "closed"
        if self.clock() - self._opened_at >= self.cooldown:
            return "half-open"
        return "open"

    def call(self, fn, *args, **kwargs):
        state = self.state
        if state == "open":
            raise CircuitOpen("circuit is open: failing fast")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            if state == "half-open":
                self._opened_at = self.clock()          # the trial failed: open again
            else:
                self._failures += 1
                if self._failures >= self.threshold:
                    self._opened_at = self.clock()
            raise
        self._failures = 0
        self._opened_at = None
        return result
