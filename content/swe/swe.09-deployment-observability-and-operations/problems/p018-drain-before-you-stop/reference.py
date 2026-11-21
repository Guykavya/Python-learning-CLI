import contextlib
import threading
import time


class Lifecycle:
    def __init__(self, clock=time.monotonic, sleep=time.sleep):
        self._clock, self._sleep = clock, sleep
        self._lock = threading.Lock()
        self._draining = False
        self._in_flight = 0

    @property
    def draining(self):
        return self._draining

    @property
    def in_flight(self):
        with self._lock:
            return self._in_flight

    def on_sigterm(self):
        self._draining = True                                   # readiness goes red; running requests continue

    @contextlib.contextmanager
    def track(self):
        with self._lock:
            self._in_flight += 1
        try:
            yield
        finally:
            with self._lock:
                self._in_flight -= 1

    def readiness(self):
        if self._draining:
            return 503, {"status": "not ready", "problems": {"draining": "shutting down"}}
        return 200, {"status": "ready"}

    def wait_idle(self, timeout, poll=0.1):
        deadline = self._clock() + timeout
        while self.in_flight > 0:
            remaining = deadline - self._clock()
            if remaining <= 0:
                return False
            self._sleep(min(poll, remaining))
        return True
