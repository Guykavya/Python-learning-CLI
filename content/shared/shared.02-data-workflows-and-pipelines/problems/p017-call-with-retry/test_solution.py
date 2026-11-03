import logging
import time

import httpx
import pytest

from solution import call_with_retry

BASE = "https://api.pagebound.test"


@pytest.fixture(autouse=True)
def no_real_sleeping(monkeypatch):
    def boom(seconds):
        raise AssertionError(
            "time.sleep was called directly. Call the 'sleep' PARAMETER so tests (and callers) "
            "control the waiting."
        )
    monkeypatch.setattr(time, "sleep", boom)


class FakeSleep:
    def __init__(self):
        self.delays = []

    def __call__(self, seconds):
        self.delays.append(seconds)


def scripted(*answers):
    """Handler answering in order. An answer is a status, (status, headers) or an exception class."""
    calls = []

    def handler(request):
        answer = answers[min(len(calls), len(answers) - 1)]
        calls.append(request)
        if isinstance(answer, type) and issubclass(answer, Exception):
            raise answer("simulated failure", request=request)
        status, headers = answer if isinstance(answer, tuple) else (answer, {})
        body = {"data": [{"id": 101}], "page": 1, "next_page": None} if status < 400 else {"error": status}
        return httpx.Response(status, json=body, headers=headers)

    return handler, calls


def call(handler, rand=lambda: 1.0, **kwargs):
    sleep = FakeSleep()
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE)
    result = call_with_retry(client, "/v1/orders", {"page": 2}, sleep=sleep, rand=rand, **kwargs)
    return result, sleep


def test_success_first_time():
    handler, calls = scripted(200)
    result, sleep = call(handler)
    assert result == {"data": [{"id": 101}], "page": 1, "next_page": None}, (
        "Return the decoded JSON (response.json()), not the Response object."
    )
    assert len(calls) == 1 and sleep.delays == [], "One success: one request, no sleeping."


def test_sends_path_and_params():
    handler, calls = scripted(200)
    call(handler)
    assert calls[0].url.path == "/v1/orders" and calls[0].url.params["page"] == "2", (
        "Send GET <path> with the given params through the client."
    )


def test_5xx_backoff_doubles():
    handler, calls = scripted(503, 502, 200)
    result, sleep = call(handler)
    assert result["data"] == [{"id": 101}], "The third attempt succeeds; return its JSON."
    assert len(calls) == 3, f"Expected 3 requests, the server saw {len(calls)}."
    assert sleep.delays == pytest.approx([1.0, 2.0]), (
        f"Delays {sleep.delays}. With rand() = 1.0 the delay is the full backoff: "
        "base_delay * 2**(k-1) = 1.0, then 2.0. Call the sleep parameter."
    )


def test_jitter_uses_rand():
    handler, _ = scripted(500, 500, 200)
    _, sleep = call(handler, rand=lambda: 0.0)
    assert sleep.delays == pytest.approx([0.5, 1.0]), (
        f"Delays {sleep.delays} with rand() = 0.0. Equal jitter is backoff/2 + rand()*backoff/2, "
        "so the smallest possible delays are 0.5 and 1.0. Use the rand PARAMETER."
    )
    handler, _ = scripted(500, 500, 200)
    _, sleep = call(handler, rand=lambda: 0.5)
    assert sleep.delays == pytest.approx([0.75, 1.5]), f"Delays {sleep.delays} with rand() = 0.5."


def test_429_is_retried_and_retry_after_is_obeyed_exactly():
    handler, calls = scripted((429, {"Retry-After": "7"}), 200)
    _, sleep = call(handler, rand=lambda: 0.0)
    assert len(calls) == 2, "429 means 'slow down', not 'never': retry it."
    assert sleep.delays == pytest.approx([7.0]), (
        f"Delays {sleep.delays}. The server said Retry-After: 7, so wait exactly 7 seconds: "
        "no jitter and no backoff formula."
    )


def test_retry_after_on_503_too():
    handler, _ = scripted((503, {"Retry-After": "3"}), (503, {"Retry-After": "5"}), 200)
    _, sleep = call(handler)
    assert sleep.delays == pytest.approx([3.0, 5.0]), (
        f"Delays {sleep.delays}. Read Retry-After from EACH failed response."
    )


def test_retry_after_is_capped_by_max_delay():
    handler, _ = scripted((429, {"Retry-After": "120"}), 200)
    _, sleep = call(handler)
    assert sleep.delays == pytest.approx([30.0]), (
        f"Delays {sleep.delays}. Never wait longer than max_delay (30): use min(120, 30)."
    )


def test_retry_after_http_date_is_ignored():
    handler, _ = scripted((503, {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}), 200)
    _, sleep = call(handler)
    assert sleep.delays == pytest.approx([1.0]), (
        f"Delays {sleep.delays}. A Retry-After that is not a whole number of seconds is ignored; "
        "fall back to the backoff (1.0 here). int() on a date must not crash your helper."
    )


def test_gives_up_after_max_attempts():
    handler, calls = scripted(500, 500, 500, 500, 200)
    with pytest.raises(httpx.HTTPStatusError) as info:
        call(handler, base_delay=10.0)
    assert len(calls) == 4, f"max_attempts=4 means 4 requests in total; the server saw {len(calls)}."
    assert info.value.response.status_code == 500


def test_cap_values():
    handler, _ = scripted(500, 500, 500, 500)
    sleep = FakeSleep()
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE)
    with pytest.raises(httpx.HTTPStatusError):
        call_with_retry(client, "/v1/orders", base_delay=10.0, sleep=sleep, rand=lambda: 1.0)
    assert sleep.delays == pytest.approx([10.0, 20.0, 30.0]), (
        f"Delays {sleep.delays}. 10, 20, then 40 capped to max_delay 30. And no sleep after the "
        "4th (last) attempt: 3 sleeps."
    )


def test_raises_the_error_of_the_last_attempt():
    handler, _ = scripted(500, 502, 503, 504)
    with pytest.raises(httpx.HTTPStatusError) as info:
        call(handler)
    assert info.value.response.status_code == 504, (
        "Raise the LAST attempt's error (504), not the first one and not a new exception type."
    )


def test_client_errors_are_not_retried():
    for status in (400, 401, 403, 404, 409, 422):
        handler, calls = scripted(status, 200)
        with pytest.raises(httpx.HTTPStatusError):
            call(handler)
        assert len(calls) == 1, (
            f"Status {status} was retried. Only 429 and 5xx are temporary; other 4xx mean the "
            "request is wrong and will fail the same way again."
        )


def test_transport_errors_are_retried():
    handler, calls = scripted(httpx.ConnectError, httpx.ReadTimeout, 200)
    result, sleep = call(handler)
    assert result["data"] == [{"id": 101}] and len(calls) == 3, (
        "ConnectError and ReadTimeout are httpx.TransportError: temporary, so retry them."
    )
    assert sleep.delays == pytest.approx([1.0, 2.0])


def test_transport_error_every_time_raises_it():
    handler, calls = scripted(httpx.ConnectError)
    with pytest.raises(httpx.ConnectError):
        call(handler, max_attempts=3)
    assert len(calls) == 3, f"max_attempts=3 allows 3 requests; the server saw {len(calls)}."


def test_max_attempts_one_means_no_retry():
    handler, calls = scripted(503, 200)
    with pytest.raises(httpx.HTTPStatusError):
        _, sleep = call(handler, max_attempts=1)
    assert len(calls) == 1, "max_attempts=1: try once, never retry."


def test_bugs_are_not_retried():
    calls = []

    def handler(request):
        calls.append(request)
        raise ValueError("a bug in the handler, not a network problem")

    with pytest.raises(ValueError):
        call(handler)
    assert len(calls) == 1, (
        "A ValueError was retried. Catch only httpx.HTTPStatusError and httpx.TransportError, "
        "never every Exception: retrying a bug hides it."
    )


def test_one_warning_per_retry(caplog):
    caplog.set_level(logging.WARNING, logger="pipeline")
    handler, _ = scripted(503, (429, {"Retry-After": "2"}), 200)
    call(handler)
    warnings = [r for r in caplog.records if r.name == "pipeline" and r.levelno == logging.WARNING]
    assert len(warnings) == 2, (
        f"{len(warnings)} warnings on logger 'pipeline'; expected one per retry (2). Use "
        "logging.getLogger('pipeline').warning(...), not print."
    )


def test_no_log_on_success(caplog):
    caplog.set_level(logging.DEBUG, logger="pipeline")
    handler, _ = scripted(200)
    call(handler)
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING], (
        "A successful first attempt is not worth a warning."
    )
