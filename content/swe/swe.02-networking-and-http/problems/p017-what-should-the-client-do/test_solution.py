from datetime import datetime, timezone

import pytest

from solution import client_action

NOW = datetime(2026, 11, 7, 10, 0, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize("status", [200, 201, 204, 304])
def test_use(status):
    assert client_action(status, {}, NOW) == "use"


def test_redirects():
    assert client_action(301, {"location": "/new"}, NOW) == "follow:/new"
    assert client_action(302, {"Location": "https://x.example/a"}, NOW) == "follow:https://x.example/a"
    assert client_action(307, {"LOCATION": "/t"}, NOW) == "follow:/t", "Header names ignore case."
    assert client_action(308, {}, NOW) == "give-up", "A redirect with no Location has nowhere to go."


def test_retry_after_in_seconds():
    assert client_action(503, {"Retry-After": "30"}, NOW) == "wait:30"
    assert client_action(429, {"retry-after": "0"}, NOW) == "wait:0"


def test_retry_after_as_a_date_rounds_up():
    assert client_action(503, {"Retry-After": "Sat, 07 Nov 2026 10:00:30 GMT"}, NOW) == "wait:30"
    half = datetime(2026, 11, 7, 10, 0, 0, 500000, tzinfo=timezone.utc)
    assert client_action(503, {"Retry-After": "Sat, 07 Nov 2026 10:00:30 GMT"}, half) == "wait:30", (
        "29.5 seconds remain: round UP to 30, never wake up early.")
    assert client_action(503, {"Retry-After": "Sat, 07 Nov 2026 09:00:00 GMT"}, NOW) == "wait:0", "A date in the past is 0."


def test_missing_or_bad_retry_after_means_retry():
    assert client_action(429, {}, NOW) == "retry"
    assert client_action(503, {"Retry-After": "soon"}, NOW) == "retry"
    assert client_action(503, {"Retry-After": ""}, NOW) == "retry"


@pytest.mark.parametrize("status", [408, 500, 502, 504])
def test_retry(status):
    assert client_action(status, {}, NOW) == "retry"


def test_log_in_and_fix_request():
    assert client_action(401, {}, NOW) == "log-in"
    for s in (400, 404, 405, 409, 410, 415, 422):
        assert client_action(s, {}, NOW) == "fix-request", f"{s} means the request is wrong: fix it, do not retry."


@pytest.mark.parametrize("status", [403, 418, 501, 100, 505])
def test_give_up(status):
    assert client_action(status, {}, NOW) == "give-up"


def test_now_defaults_to_the_current_time():
    far_future = "Fri, 01 Jan 2100 00:00:00 GMT"
    out = client_action(503, {"Retry-After": far_future})
    assert out.startswith("wait:") and int(out[5:]) > 10**9, "Without 'now' use the real current UTC time."
