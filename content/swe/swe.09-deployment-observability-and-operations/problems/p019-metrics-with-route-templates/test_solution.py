import re
import time

import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

from solution import BUCKETS, Metrics


def parse(text):
    """Prometheus text -> {(name, ((label, value), ...)): float}."""
    samples = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        head, value = line.rsplit(" ", 1)
        name, _, rest = head.partition("{")
        labels = tuple(sorted(re.findall(r'(\w+)="([^"]*)"', rest)))
        samples[(name, labels)] = float(value)
    return samples


def sample(samples, name, **labels):
    return samples.get((name, tuple(sorted(labels.items()))))


class MetricsMiddleware:
    """What the service wraps around the app: it measures every request and hands the scope to observe_request."""

    def __init__(self, app, metrics):
        self.app, self.metrics = app, metrics

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started, status = time.perf_counter(), 500

        async def send_wrapper(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        self.metrics.in_flight += 1
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            self.metrics.in_flight -= 1
            self.metrics.observe_request(scope, status, time.perf_counter() - started)


@pytest.fixture
def parts():
    metrics = Metrics()
    app = FastAPI()
    app.add_middleware(MetricsMiddleware, metrics=metrics)

    @app.get("/orders/{order_id}")
    def get_order(order_id: int):
        from fastapi import HTTPException
        raise HTTPException(404, "order not found")

    @app.post("/orders", status_code=201)
    def create_order():
        return {"id": 1}

    @app.get("/boom")
    def boom():
        raise RuntimeError("simulated bug")

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics_endpoint():
        return metrics.render()

    return metrics, TestClient(app, raise_server_exceptions=False)


def test_observe_counts_requests():
    m = Metrics()
    m.observe("GET", "/orders/{order_id}", 404, 0.002)
    m.observe("GET", "/orders/{order_id}", 404, 0.002)
    m.observe("POST", "/orders", 201, 0.3)
    s = parse(m.render())
    assert sample(s, "http_requests_total", method="GET", route="/orders/{order_id}", status="404") == 2, "The counter is split by method, route and status."
    assert sample(s, "http_requests_total", method="POST", route="/orders", status="201") == 1


def test_histogram_buckets_are_cumulative():
    m = Metrics()
    for seconds in (0.002, 0.04, 0.6):
        m.observe("GET", "/slow", 200, seconds)
    s = parse(m.render())
    expected = {"0.005": 1, "0.01": 1, "0.025": 1, "0.05": 2, "0.1": 2, "0.25": 2, "0.5": 2, "1.0": 3, "2.5": 3, "5.0": 3, "10.0": 3, "+Inf": 3}
    got = {le: sample(s, "http_request_duration_seconds_bucket", method="GET", route="/slow", le=le) for le in expected}
    assert got == expected, f"Cumulative buckets: an observation counts in EVERY bucket whose upper bound is >= its value; got {got}"


def test_sum_and_count():
    m = Metrics()
    m.observe("GET", "/x", 200, 0.25)
    m.observe("GET", "/x", 200, 0.5)
    s = parse(m.render())
    assert sample(s, "http_request_duration_seconds_sum", method="GET", route="/x") == pytest.approx(0.75)
    assert sample(s, "http_request_duration_seconds_count", method="GET", route="/x") == 2
    assert "http_request_duration_seconds_sum{method=\"GET\",route=\"/x\"} 0.750000\n" in m.render(), "_sum is written with 6 decimals."


def test_boundary_value_goes_into_its_own_bucket():
    m = Metrics()
    m.observe("GET", "/x", 200, 0.1)
    s = parse(m.render())
    assert sample(s, "http_request_duration_seconds_bucket", method="GET", route="/x", le="0.1") == 1, "le means 'less than or equal': 0.1 is in the 0.1 bucket."
    assert sample(s, "http_request_duration_seconds_bucket", method="GET", route="/x", le="0.05") == 0


def test_text_layout():
    m = Metrics()
    m.observe("GET", "/a", 200, 0.002)
    text = m.render()
    assert text.endswith("\n") and not text.endswith("\n\n"), "One final newline."
    for line in ("# TYPE http_requests_total counter", "# TYPE http_request_duration_seconds histogram", "# TYPE http_requests_in_flight gauge"):
        assert line in text.splitlines(), f"Missing the line {line!r}"
    assert 'http_request_duration_seconds_bucket{method="GET",route="/a",le="0.005"} 1' in text, "Label order: method, route, then le."
    assert 'http_request_duration_seconds_bucket{method="GET",route="/a",le="10.0"} 1' in text, "le values are str() of the bucket bounds: 0.005 ... 1.0, 2.5, 5.0, 10.0."


def test_series_are_sorted():
    m = Metrics()
    m.observe("POST", "/b", 201, 0.1)
    m.observe("GET", "/b", 500, 0.1)
    m.observe("GET", "/a", 200, 0.1)
    counters = [l for l in m.render().splitlines() if l.startswith("http_requests_total")]
    assert counters == sorted(counters) and len(counters) == 3, "Counter lines are sorted by (method, route, status)."


def test_in_flight_gauge():
    m = Metrics()
    assert "http_requests_in_flight 0\n" in m.render()
    m.in_flight = 3
    assert "http_requests_in_flight 3\n" in m.render(), "The gauge shows the current value of the attribute."


def test_route_templates_not_raw_paths(parts):
    metrics, client = parts
    client.get("/orders/1")
    client.get("/orders/2")
    client.get("/orders/3")
    text = client.get("/metrics").text
    assert 'route="/orders/{order_id}"' in text, "The label holds the route TEMPLATE."
    assert "/orders/1" not in text and "/orders/2" not in text, \
        "Raw paths would create one time series per order id and finally exhaust the monitoring system (the cardinality trap)."
    s = parse(text)
    assert sample(s, "http_requests_total", method="GET", route="/orders/{order_id}", status="404") == 3


def test_unmatched_paths_share_one_label(parts):
    metrics, client = parts
    for path in ("/nothing", "/wp-login.php", "/.env"):
        client.get(path)
    s = parse(client.get("/metrics").text)
    assert sample(s, "http_requests_total", method="GET", route="unmatched", status="404") == 3, \
        "Paths that match no route (scanners!) all go into the single label 'unmatched'."


def test_server_errors_are_counted(parts):
    metrics, client = parts
    client.get("/boom")
    s = parse(client.get("/metrics").text)
    assert sample(s, "http_requests_total", method="GET", route="/boom", status="500") == 1, "A request that failed with an exception counts as a 500."


def test_in_flight_is_back_to_zero_after_requests(parts):
    metrics, client = parts
    client.post("/orders")
    assert metrics.in_flight == 0
