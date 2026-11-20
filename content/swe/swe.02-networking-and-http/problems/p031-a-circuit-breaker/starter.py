class CircuitOpen(Exception):
    pass


class CircuitBreaker:
    def __init__(self, threshold, cooldown, clock):
        self.threshold = threshold
        self.cooldown = cooldown
        self.clock = clock

    @property
    def state(self):
        return "closed"

    def call(self, fn, *args, **kwargs):
        # TODO: closed / open / half-open as described in the statement
        return fn(*args, **kwargs)
