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
            return "503"                                        # refused: the state does not change
        self.excess, self.last = new_excess, t
        return "pass" if new_excess == 0 or self.nodelay else "delayed"
