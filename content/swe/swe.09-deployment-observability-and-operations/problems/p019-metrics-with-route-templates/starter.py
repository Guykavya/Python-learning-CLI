import threading
from collections import defaultdict

BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.requests = defaultdict(int)                              # (method, route, status) -> count
        self.bucket_counts = defaultdict(lambda: [0] * len(BUCKETS))   # (method, route) -> cumulative bucket counts
        self.sums = defaultdict(float)
        self.counts = defaultdict(int)
        self.in_flight = 0

    def observe(self, method, route, status, seconds):
        # TODO
        pass

    def observe_request(self, scope, status, seconds):
        # TODO: the route TEMPLATE from scope["route"], or "unmatched"
        pass

    def render(self):
        # TODO: the Prometheus text of problem.md
        return ""
