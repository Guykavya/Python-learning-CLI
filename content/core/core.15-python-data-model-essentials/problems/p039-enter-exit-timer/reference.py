import time


class Timer:
    def __init__(self, clock=time.perf_counter):
        self.clock = clock
        self._start = None
        self._elapsed = 0.0
        self.running = False

    def __enter__(self):
        self._start = self.clock()
        self.running = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self._elapsed = self.clock() - self._start
        self.running = False
        return False

    @property
    def elapsed(self):
        if self.running:
            return self.clock() - self._start
        return self._elapsed
