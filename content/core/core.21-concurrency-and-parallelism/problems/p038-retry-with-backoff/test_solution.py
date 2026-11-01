import asyncio

import httpx
import pytest

from solution import get_with_retry

URL = "https://api.test/data"


class FakeSleep:
    def __init__(self):
        self.delays = []

    async def __call__(self, delay):
        self.delays.append(delay)


def scripted(*answers):
    """Handler that gives the answers in order: an int status or an exception class."""
    calls = []

    def handler(request):
        answer = answers[min(len(calls), len(answers) - 1)]
        calls.append(answer)
        if isinstance(answer, int):
            return httpx.Response(answer, text=f"status {answer}")
        raise answer("simulated network problem", request=request)

    return handler, calls


def run(handler, **kwargs):
    sleep = FakeSleep()

    async def main():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await get_with_retry(client, URL, sleep=sleep, **kwargs)

    return asyncio.run(main()), sleep


def test_success_first_time_does_not_sleep():
    handler, calls = scripted(200)
    response, sleep = run(handler)
    assert isinstance(response, httpx.Response) and response.status_code == 200, (
        "Return the httpx.Response itself when the request succeeds."
    )
    assert len(calls) == 1, f"{len(calls)} requests were sent; one success needs one request."
    assert sleep.delays == [], f"Slept {sleep.delays} after a success. Only sleep before a retry."


def test_retries_5xx_then_succeeds():
    handler, calls = scripted(503, 502, 200)
    response, sleep = run(handler)
    assert response.status_code == 200, "After two 5xx answers the third attempt succeeds."
    assert len(calls) == 3, f"Expected 3 requests, the server saw {len(calls)}."
    assert sleep.delays == pytest.approx([0.1, 0.2]), (
        f"Delays were {sleep.delays}. Use base_delay * 2**attempt (0.1, 0.2, ...) and call the "
        "'sleep' PARAMETER, not asyncio.sleep, so the test can record it."
    )


def test_gives_up_after_retries_and_raises_the_last_error():
    handler, calls = scripted(500, 500, 500, 503)
    with pytest.raises(httpx.HTTPStatusError) as info:
        run(handler)
    assert len(calls) == 4, (
        f"The server saw {len(calls)} requests. retries=3 means 1 first try + 3 retries = 4."
    )
    assert info.value.response.status_code == 503, (
        "Raise the error of the LAST attempt (503 here), not the first one."
    )


def test_no_sleep_after_the_last_attempt():
    handler, _ = scripted(500)
    sleep = FakeSleep()

    async def main():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await get_with_retry(client, URL, sleep=sleep)

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(main())
    assert sleep.delays == pytest.approx([0.1, 0.2, 0.4]), (
        f"Delays were {sleep.delays}. Sleep before each RETRY only: 3 retries = 3 sleeps, and "
        "no pointless sleep after the final failure."
    )


def test_4xx_is_not_retried():
    handler, calls = scripted(404, 200)
    with pytest.raises(httpx.HTTPStatusError) as info:
        run(handler)
    assert len(calls) == 1, (
        f"A 404 was retried ({len(calls)} requests). 4xx means the request itself is wrong; "
        "retrying cannot help, so raise at once."
    )
    assert info.value.response.status_code == 404


def test_other_4xx_not_retried_either():
    for status in (400, 401, 403, 429):
        handler, calls = scripted(status, 200)
        with pytest.raises(httpx.HTTPStatusError):
            run(handler)
        assert len(calls) == 1, f"Status {status} was retried. Only 5xx (>= 500) is retried."


def test_transport_error_is_retried():
    handler, calls = scripted(httpx.ConnectError, httpx.ReadError, 200)
    response, sleep = run(handler)
    assert response.status_code == 200, (
        "ConnectError and ReadError are httpx.TransportError subclasses: retry them."
    )
    assert len(calls) == 3
    assert sleep.delays == pytest.approx([0.1, 0.2])


def test_transport_error_every_time_raises_it():
    handler, calls = scripted(httpx.ConnectError)
    with pytest.raises(httpx.ConnectError):
        run(handler, retries=2)
    assert len(calls) == 3, f"retries=2 allows 3 attempts; the server saw {len(calls)}."


def test_retries_zero_means_one_attempt():
    handler, calls = scripted(503, 200)
    with pytest.raises(httpx.HTTPStatusError):
        run(handler, retries=0)
    assert len(calls) == 1, "retries=0 means: try once, never retry."


def test_base_delay_is_used():
    handler, _ = scripted(500, 500, 500, 200)
    _, sleep = run(handler, base_delay=1.5)
    assert sleep.delays == pytest.approx([1.5, 3.0, 6.0]), (
        f"Delays were {sleep.delays}; with base_delay=1.5 they must be 1.5, 3.0, 6.0."
    )


def test_other_exceptions_are_not_caught():
    def handler(request):
        raise ValueError("a bug, not a network problem")

    with pytest.raises(ValueError):
        run(handler)
    # Catching every Exception would also retry real bugs and hide them.
