class LimitReq:
    def __init__(self, rate_per_s, burst=0, nodelay=False):
        self.rate, self.burst, self.nodelay = rate_per_s, burst, nodelay
        self.excess, self.last = 0.0, None

    def allow(self, t):
        # TODO: the four steps of problem.md
        return "pass"
