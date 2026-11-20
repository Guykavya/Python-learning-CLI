import pytest
from fastapi.testclient import TestClient

from solution import RateLimit, create_app, get_clock


class FakeClock:
    def __init__(self):
        self.now = 0.0


@pytest.fixture
def env():
    app = create_app()
    clock = FakeClock()
    app.dependency_overrides[get_clock] = lambda: clock.now
    try:
        with TestClient(app) as client:
            yield app, clock, client
    finally:
        app.dependency_overrides.clear()


def call(env, t, path="/search", key="k1"):
    _, clock, client = env
    clock.now = t
    return client.get(path, headers={"X-API-Key": key})


def test_under_the_limit_is_200(env):
    r = call(env, 0)
    assert r.status_code == 200, f"The first request is allowed, got {r.status_code}: {r.text}"
    assert r.json() == {"key": "k1", "results": []}, f"The dependency returns the key to the endpoint; got {r.json()}"


def test_fourth_call_in_the_window_is_429_with_retry_after(env):
    for t in (0, 10, 20):
        assert call(env, t).status_code == 200, f"Request at t={t} is one of the first three: allowed."
    r = call(env, 25)
    assert r.status_code == 429, f"The 4th request within 60 s must be refused with 429, got {r.status_code}"
    assert r.json() == {"detail": "Rate limit exceeded"}, f"Got {r.json()}"
    assert r.headers.get("retry-after") == "35", (
        f"The oldest request (t=0) stops counting at t=60, so Retry-After is 60-25 = 35; got {r.headers.get('retry-after')!r}")


def test_rejected_calls_are_not_recorded(env):
    for t in (0, 10, 20):
        call(env, t)
    for _ in range(5):
        call(env, 25)
    r = call(env, 60)
    assert r.status_code == 200, (
        f"At t=60 the request from t=0 has expired, so a slot is free; got {r.status_code}. "
        "Do not record a request that you refused.")


def test_the_window_slides(env):
    for t in (0, 10, 20):
        call(env, t)
    assert call(env, 59.9).status_code == 429, "At t=59.9 the request from t=0 still counts (59.9 - 0 < 60)."
    assert call(env, 60).status_code == 200, "At t=60 the request from t=0 no longer counts (60 - 0 < 60 is false)."
    r = call(env, 61)
    assert r.status_code == 429, "Now counting t=10, 20, 60: full again."
    assert r.headers.get("retry-after") == "9", f"Oldest is t=10: 10 + 60 - 61 = 9; got {r.headers.get('retry-after')!r}"


def test_retry_after_is_rounded_up_and_at_least_1(env):
    for _ in range(3):
        call(env, 0)
    r = call(env, 59.5)
    assert r.headers.get("retry-after") == "1", (
        f"0 + 60 - 59.5 = 0.5 seconds: round UP with math.ceil, so 1; got {r.headers.get('retry-after')!r}")
    r = call(env, 30.2)
    assert r.headers.get("retry-after") == "30", f"0 + 60 - 30.2 = 29.8, rounded up: 30; got {r.headers.get('retry-after')!r}"


def test_keys_are_counted_separately(env):
    for t in (0, 1, 2):
        call(env, t, key="k1")
    assert call(env, 3, key="k1").status_code == 429
    assert call(env, 3, key="k2").status_code == 200, "Key k2 has made no requests yet: allowed. Keep one list per key."


def test_each_endpoint_has_its_own_limiter(env):
    assert call(env, 0, "/export").status_code == 200
    r = call(env, 5, "/export")
    assert r.status_code == 429, f"/export allows 1 request per 10 s; the second at t=5 is 429, got {r.status_code}"
    assert r.headers.get("retry-after") == "5", f"0 + 10 - 5 = 5; got {r.headers.get('retry-after')!r}"
    assert call(env, 5, "/search").status_code == 200, "/search has its own RateLimit(3, 60) instance with its own counts."
    assert call(env, 10, "/export").status_code == 200, "At t=10 the /export request from t=0 has expired."


def test_missing_key_is_422(env):
    _, _, client = env
    r = client.get("/search")
    assert r.status_code == 422, f"X-API-Key is required: 422, got {r.status_code}"
    assert [(e["loc"], e["type"]) for e in r.json()["detail"]] == [(["header", "x-api-key"], "missing")], r.json()


def test_new_app_starts_clean(env):
    for t in (0, 1, 2, 3):
        call(env, t)
    other = create_app()
    other.dependency_overrides[get_clock] = lambda: 4.0
    with TestClient(other) as client:
        r = client.get("/search", headers={"X-API-Key": "k1"})
    assert r.status_code == 200, "create_app() must build new RateLimit objects, so a new app has no old counts."


def test_ratelimit_is_reusable_directly():
    limiter = RateLimit(2, 10)
    assert limiter("a", 0.0) == "a" and limiter("a", 1.0) == "a", "Calling the object directly records and returns the key."
    with pytest.raises(Exception) as info:
        limiter("a", 2.0)
    assert getattr(info.value, "status_code", None) == 429, "The third call within 10 s raises HTTPException(429)."
