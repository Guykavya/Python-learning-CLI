## Approach

```python
class Metrics:
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
        route = getattr(scope.get("route"), "path", "unmatched")
        self.observe(scope["method"], route, status, seconds)
```

and `render()` builds the lines as in `reference.py`. Three ideas to keep:

- **Cumulative buckets**: a request of 0.6 s counts in `le="1.0"` and in every larger bucket, so each bucket line answers "how many requests were at most this slow?". That is what lets `histogram_quantile` (problem p020) estimate percentiles.
- **Template, not path**: every distinct label combination is a separate time series. `/orders/1`, `/orders/2`, ... would create one series per order id. The template gives one series; scanner traffic to random URLs all goes to `unmatched`.
- **Locking**: the service handles several requests at once, and `render()` runs while they are being observed.

## Complexity

`observe` is O(number of buckets) = 11. `render` is O(number of series x buckets). Memory is proportional to the number of distinct `(method, route, status)` combinations, which is why the labels must stay few.

## Another way

The `prometheus-client` package (not installed in this course) provides `Counter`, `Gauge` and `Histogram` with the same text format. This hand-written registry shows what they do, and what the cardinality rule protects.
