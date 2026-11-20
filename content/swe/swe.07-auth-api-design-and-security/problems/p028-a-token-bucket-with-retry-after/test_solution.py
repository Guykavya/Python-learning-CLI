import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from solution import TokenBucket, rate_limit


class Clock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


def test_a_new_bucket_is_full_and_allows_a_burst():
    clock = Clock()
    b = TokenBucket(3, 0.5, clock)
    got = [b.take() for _ in range(3)]
    assert got == [(True, 0)] * 3, f"A full bucket of 3 allows 3 requests at once and returns (True, 0) each time; got {got}"


def test_empty_bucket_refuses_and_says_how_long():
    clock = Clock()
    b = TokenBucket(3, 0.5, clock)
    for _ in range(3):
        b.take()
    assert b.take() == (False, 2), "Empty bucket, rate 0.5/s: one token needs 2 seconds, so (False, 2)"


def test_retry_after_shrinks_as_time_passes_and_the_token_comes_back():
    clock = Clock()
    b = TokenBucket(3, 0.5, clock)
    for _ in range(3):
        b.take()
    b.take()
    clock.t = 1.0
    assert b.take() == (False, 1), "After 1 s half a token exists (rate 0.5): 1 more second is needed -> (False, 1)"
    clock.t = 2.0
    assert b.take() == (True, 0), "After 2 s one whole token is back: the request must pass"
    assert b.take() == (False, 2), "That token is used up again: the bucket is empty, wait 2 s"


def test_retry_after_is_rounded_up_never_zero():
    clock = Clock()
    b = TokenBucket(1, 2.0, clock)
    assert b.take() == (True, 0)
    allowed, wait = b.take()
    assert allowed is False and wait == 1, (
        f"Rate 2/s: the missing token needs 0.5 s. Retry-After is a whole number, rounded UP to 1 (math.ceil); got {wait!r}")
    clock.t = 0.25
    assert b.take() == (False, 1), "Half the wait has passed (0.25 s left): still rounds up to 1, never down to 0"


def test_whole_seconds_use_ceil_on_a_slow_rate():
    clock = Clock()
    b = TokenBucket(1, 0.25, clock)
    b.take()
    assert b.take() == (False, 4), "Rate 0.25/s: one token needs 4 seconds"
    clock.t = 1.0
    assert b.take() == (False, 3), "After 1 s, 0.25 tokens exist; 0.75 are missing = 3 seconds"


def test_refused_requests_use_nothing_up():
    clock = Clock()
    b = TokenBucket(2, 0.5, clock)
    b.take()
    b.take()
    for _ in range(20):
        assert b.take()[0] is False
    clock.t = 2.0
    assert b.take() == (True, 0), (
        "20 refused calls must not make the wait longer: at t=2 s one token exists and the request must pass. "
        "Do not subtract a token when you refuse.")


def test_refill_is_capped_at_capacity():
    clock = Clock()
    b = TokenBucket(5, 0.5, clock)
    for _ in range(5):
        b.take()
    clock.t = 1_000.0
    allowed = [b.take()[0] for _ in range(8)]
    assert allowed == [True] * 5 + [False] * 3, (
        f"After a long idle time the bucket holds at most capacity (5) tokens, so exactly 5 requests pass; got {allowed}. "
        "Use min(capacity, tokens + ...).")


def test_partial_refill_is_remembered_between_calls():
    clock = Clock()
    b = TokenBucket(2, 0.5, clock)
    b.take()
    b.take()
    clock.t = 1.0
    assert b.take()[0] is False
    clock.t = 2.0
    assert b.take()[0] is True, (
        "Half a token at t=1 plus half a token at t=2 makes one whole token. Update `last` after every call, "
        "and do not throw the fraction away.")


def test_a_second_bucket_does_not_share_state():
    clock = Clock()
    a, b = TokenBucket(1, 1.0, clock), TokenBucket(1, 1.0, clock)
    a.take()
    assert b.take() == (True, 0), "Each bucket has its own tokens: keep them on self, not in a global"


def make_client(capacity, rate, clock):
    app = FastAPI()
    bucket = TokenBucket(capacity, rate, clock)

    @app.get("/ping", dependencies=[Depends(rate_limit(bucket))])
    def ping():
        return {"ok": True}

    return TestClient(app)


def test_http_429_with_retry_after_header():
    clock = Clock()
    with make_client(2, 0.5, clock) as client:
        assert client.get("/ping").status_code == 200
        assert client.get("/ping").status_code == 200
        r = client.get("/ping")
        assert r.status_code == 429, f"The third request in a burst of capacity 2 must be refused with 429, got {r.status_code}"
        assert r.headers.get("retry-after") == "2", (
            f"Send the header Retry-After with the wait in seconds as text ('2'); got {r.headers.get('retry-after')!r}")


def test_http_recovers_after_the_wait():
    clock = Clock()
    with make_client(1, 0.5, clock) as client:
        assert client.get("/ping").status_code == 200
        assert client.get("/ping").status_code == 429
        clock.t = 1.0
        r = client.get("/ping")
        assert r.status_code == 429 and r.headers["retry-after"] == "1", "After 1 s the wait is down to 1 s"
        clock.t = 2.0
        assert client.get("/ping").status_code == 200, "After the advertised wait the request must pass"
