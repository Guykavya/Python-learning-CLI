# Metrics with route templates

Chapter sections 10.1 (logs tell stories, metrics tell trends), 10.2 (what the service exposes, and the cardinality trap) and 5.1 (`metrics.py`). Write the small registry that a service exposes on `/metrics` in the **Prometheus text format**. Prometheus reads this text every few seconds; you will see why the `route` label must be the route **template** (`/orders/{order_id}`), never the raw path (`/orders/1234`).

## What to write

```python
BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)      # given

class Metrics:
    in_flight: int                                   # a plain attribute, starts at 0
    def observe(self, method, route, status, seconds): ...
    def observe_request(self, scope, status, seconds): ...
    def render(self) -> str: ...
```

- `observe(method, route, status, seconds)` records one finished request:
  - the **counter** for `(method, route, str(status))` goes up by 1;
  - for `(method, route)`: the sum of seconds goes up by `seconds`, the count goes up by 1, and **every bucket whose upper bound is `>= seconds` goes up by 1** (the buckets are *cumulative*).
- `observe_request(scope, status, seconds)` is called by the middleware with the ASGI `scope`. The route is `scope["route"].path` when the scope has a `"route"` key (FastAPI puts the matched route there), and the string `"unmatched"` otherwise (a 404 for a path that matches nothing). Use `scope["method"]`. **The raw path is never used.** Then call `observe`.
- `render()` returns the text below, with a final newline. It must be safe to call while requests are being observed (use a `threading.Lock`).

```text
# HELP http_requests_total Requests handled, by method, route template and status.
# TYPE http_requests_total counter
http_requests_total{method="GET",route="/orders/{order_id}",status="404"} 2
# HELP http_request_duration_seconds Request latency.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",route="/orders/{order_id}",le="0.005"} 2
... one line per bucket, with le="0.005", "0.01", "0.025", "0.05", "0.1", "0.25", "0.5", "1.0", "2.5", "5.0", "10.0" (str of the number) ...
http_request_duration_seconds_bucket{method="GET",route="/orders/{order_id}",le="+Inf"} 2
http_request_duration_seconds_sum{method="GET",route="/orders/{order_id}"} 0.004000
http_request_duration_seconds_count{method="GET",route="/orders/{order_id}"} 2
# HELP http_requests_in_flight Requests being handled right now.
# TYPE http_requests_in_flight gauge
http_requests_in_flight 0
```

Counter lines are sorted by `(method, route, status)`, histogram groups by `(method, route)`. `le="+Inf"` equals the count; `_sum` is written with 6 decimals (`f"{value:.6f}"`).

## Example

```python
m = Metrics()
m.observe("GET", "/orders/{order_id}", 404, 0.002)
m.observe("GET", "/orders/{order_id}", 404, 0.002)
m.observe("POST", "/orders", 201, 0.3)
print(m.render())
```

The tests wrap a FastAPI app in a small ASGI middleware (given in the test file) that calls `observe_request`, send requests for `/orders/1` and `/orders/2`, and parse the text.
