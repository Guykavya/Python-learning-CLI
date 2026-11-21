import threading
from collections import defaultdict

BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.requests = defaultdict(int)
        self.bucket_counts = defaultdict(lambda: [0] * len(BUCKETS))
        self.sums = defaultdict(float)
        self.counts = defaultdict(int)
        self.in_flight = 0

    def observe(self, method, route, status, seconds):
        with self._lock:
            self.requests[(method, route, str(status))] += 1
            key = (method, route)
            self.sums[key] += seconds
            self.counts[key] += 1
            for i, upper in enumerate(BUCKETS):
                if seconds <= upper:
                    self.bucket_counts[key][i] += 1

    def observe_request(self, scope, status, seconds):
        route = getattr(scope.get("route"), "path", "unmatched")      # the TEMPLATE, never the raw path
        self.observe(scope["method"], route, status, seconds)

    def render(self):
        with self._lock:
            lines = ["# HELP http_requests_total Requests handled, by method, route template and status.",
                     "# TYPE http_requests_total counter"]
            for (method, route, status), n in sorted(self.requests.items()):
                lines.append(f'http_requests_total{{method="{method}",route="{route}",status="{status}"}} {n}')
            lines += ["# HELP http_request_duration_seconds Request latency.", "# TYPE http_request_duration_seconds histogram"]
            for (method, route), counts in sorted(self.bucket_counts.items()):
                labels = f'method="{method}",route="{route}"'
                for upper, n in zip(BUCKETS, counts):
                    lines.append(f'http_request_duration_seconds_bucket{{{labels},le="{upper}"}} {n}')
                lines.append(f'http_request_duration_seconds_bucket{{{labels},le="+Inf"}} {self.counts[(method, route)]}')
                lines.append(f'http_request_duration_seconds_sum{{{labels}}} {self.sums[(method, route)]:.6f}')
                lines.append(f'http_request_duration_seconds_count{{{labels}}} {self.counts[(method, route)]}')
            lines += ["# HELP http_requests_in_flight Requests being handled right now.", "# TYPE http_requests_in_flight gauge",
                      f"http_requests_in_flight {self.in_flight}"]
            return "\n".join(lines) + "\n"
