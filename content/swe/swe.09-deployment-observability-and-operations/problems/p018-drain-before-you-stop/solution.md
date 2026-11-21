## Approach

```python
class Lifecycle:
    def __init__(self, clock=time.monotonic, sleep=time.sleep):
        self._clock, self._sleep = clock, sleep
        self._lock = threading.Lock()
        self._draining = False
        self._in_flight = 0

    def on_sigterm(self):
        self._draining = True

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
```

The order of events in a good shutdown: `SIGTERM` arrives -> `on_sigterm()` (readiness red, the load balancer stops sending traffic) -> already running requests finish (`wait_idle`) -> the process exits before the platform's grace period ends. A flag alone is not enough: without the counter you cannot know when it is safe to exit.

## Complexity

O(1) per request. `wait_idle` polls: the cost is `timeout / poll` cheap checks. A `threading.Condition` would wake the waiter at the exact moment the last request ends instead of polling.

## Another way

Uvicorn and Gunicorn already finish in-flight requests after `SIGTERM` (chapter 9.5); this class is the **application's** half: turning readiness red first, and knowing about work that outlives a request (background tasks, open streams, WebSockets). Kubernetes adds a `preStop` sleep for the same reason: to give the load balancer time to notice.
