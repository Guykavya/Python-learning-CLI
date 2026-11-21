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
        return self._in_flight

    def on_sigterm(self):
        # TODO
        pass

    @contextlib.contextmanager
    def track(self):
        # TODO: count the request in, count it out in a finally
        yield

    def readiness(self):
        # TODO
        return 200, {"status": "ready"}

    def wait_idle(self, timeout, poll=0.1):
        # TODO
        return True
