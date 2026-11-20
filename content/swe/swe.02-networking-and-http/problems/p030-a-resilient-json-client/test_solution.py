import httpx
import pytest

from solution import RequestFailed, get_json, post_json

URL = "http://api.test/items"


class TopRng:
    def __init__(self):
        self.calls = []

    def uniform(self, a, b):
        self.calls.append((a, b))
        return b


def scripted(steps):
    """steps: list of responses or exceptions; the last one repeats. Records the requests."""
    seen = []

    def handler(request):
        step = steps[min(len(seen), len(steps) - 1)]
        seen.append(request)
        if isinstance(step, Exception):
            raise step
        return step

    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def ok(body=None):
    return httpx.Response(200, json=body if body is not None else {"ok": True})


def status(code, **headers):
    return httpx.Response(code, headers=headers, json={"e": code})


def run_get(steps, **kw):
    client, seen = scripted(steps)
    waits = []
    rng = TopRng()
    return client, seen, waits, rng, kw


def test_success_first_time():
    client, seen = scripted([ok({"a": 1})])
    waits = []
    assert get_json(client, URL, sleep=waits.append, rng=TopRng()) == {"a": 1}
    assert len(seen) == 1 and waits == [], "No failure: one request, no sleep."


def test_503_twice_then_200_with_backoff():
    client, seen = scripted([status(503), status(503), ok()])
    waits, rng = [], TopRng()
    assert get_json(client, URL, sleep=waits.append, rng=rng) == {"ok": True}
    assert len(seen) == 3
    assert rng.calls == [(0, 0.5), (0, 1.0)], f"Full jitter: rng.uniform(0, min(8, 0.5*2**k)); got {rng.calls}."
    assert waits == [0.5, 1.0], "Sleep the drawn values."


def test_connect_errors_are_retried():
    req = httpx.Request("GET", URL)
    client, seen = scripted([httpx.ConnectError("refused", request=req), httpx.ConnectTimeout("slow", request=req), ok()])
    waits = []
    assert get_json(client, URL, sleep=waits.append, rng=TopRng()) == {"ok": True}
    assert len(seen) == 3 and len(waits) == 2


def test_read_timeout_is_retried_for_get():
    req = httpx.Request("GET", URL)
    client, seen = scripted([httpx.ReadTimeout("slow", request=req), ok()])
    assert get_json(client, URL, sleep=lambda s: None, rng=TopRng()) == {"ok": True}
    assert len(seen) == 2


def test_gives_up_after_the_attempts_with_the_last_error():
    client, seen = scripted([status(503)])
    waits = []
    with pytest.raises(RequestFailed) as e:
        get_json(client, URL, attempts=3, sleep=waits.append, rng=TopRng())
    assert e.value.status == 503 and e.value.attempts == 3
    assert len(seen) == 3, "attempts=3 means three requests in all."
    assert len(waits) == 2, "No sleep after the last attempt."


def test_transport_error_at_the_end_has_no_status():
    req = httpx.Request("GET", URL)
    client, seen = scripted([httpx.ConnectError("refused", request=req)])
    with pytest.raises(RequestFailed) as e:
        get_json(client, URL, attempts=2, sleep=lambda s: None, rng=TopRng())
    assert e.value.status is None and e.value.attempts == 2


@pytest.mark.parametrize("code", [400, 401, 404, 422, 500, 501])
def test_other_errors_fail_at_once(code):
    client, seen = scripted([status(code), ok()])
    waits = []
    with pytest.raises(RequestFailed) as e:
        get_json(client, URL, sleep=waits.append, rng=TopRng())
    assert e.value.status == code and e.value.attempts == 1 and len(seen) == 1 and waits == [], (
        f"{code}: repeating the request cannot help: fail at once, with no sleep.")


def test_retry_after_is_honoured_and_capped():
    client, seen = scripted([status(429, **{"Retry-After": "7"}), status(503, **{"Retry-After": "9999"}), ok()])
    waits, rng = [], TopRng()
    assert get_json(client, URL, sleep=waits.append, rng=rng) == {"ok": True}
    assert waits == [7.0, 30.0], f"Wait what the server says, at most 30 s; got {waits}."
    assert rng.calls == [], "With Retry-After the random backoff is not used."


def test_a_body_that_is_not_json():
    client, _ = scripted([httpx.Response(200, text="<html>hi</html>")])
    with pytest.raises(RequestFailed):
        get_json(client, URL, sleep=lambda s: None, rng=TopRng())


def test_post_without_a_key_is_never_repeated_after_a_503():
    client, seen = scripted([status(503), ok()])
    with pytest.raises(RequestFailed) as e:
        post_json(client, URL, {"n": 1}, sleep=lambda s: None, rng=TopRng())
    assert len(seen) == 1 and e.value.status == 503, "A POST may have been processed: do not repeat it blindly."


def test_post_without_a_key_is_not_repeated_after_a_read_timeout():
    req = httpx.Request("POST", URL)
    client, seen = scripted([httpx.ReadTimeout("slow", request=req), ok()])
    with pytest.raises(RequestFailed):
        post_json(client, URL, {"n": 1}, sleep=lambda s: None, rng=TopRng())
    assert len(seen) == 1


def test_post_without_a_key_is_repeated_after_a_connect_error():
    req = httpx.Request("POST", URL)
    client, seen = scripted([httpx.ConnectError("refused", request=req), ok({"id": 1})])
    assert post_json(client, URL, {"n": 1}, sleep=lambda s: None, rng=TopRng()) == {"id": 1}
    assert len(seen) == 2, "A refused connection never reached the server: any method may be retried."


def test_post_with_a_key_is_retried_with_the_same_key():
    client, seen = scripted([status(503), httpx.Response(200, json={"id": 9})])
    waits = []
    assert post_json(client, URL, {"n": 1}, idempotency_key="abc-123", sleep=waits.append, rng=TopRng()) == {"id": 9}
    assert len(seen) == 2
    assert [r.headers["idempotency-key"] for r in seen] == ["abc-123", "abc-123"], "The SAME key on every attempt."
    assert b'"n"' in seen[0].content and seen[0].content == seen[1].content, "The payload is sent as JSON each time."


def test_post_sends_no_key_header_without_a_key():
    client, seen = scripted([ok()])
    post_json(client, URL, {"n": 1}, sleep=lambda s: None, rng=TopRng())
    assert "idempotency-key" not in seen[0].headers
