import asyncio

import httpx
import pytest

from solution import get_json

BASE = "https://api.example.com"


def make_handler(calls):
    def handler(request):
        calls.append((request.method, str(request.url)))
        if request.url.path == "/users/1":
            return httpx.Response(200, json={"id": 1, "name": "Asha"})
        if request.url.path == "/list":
            return httpx.Response(200, json=[1, 2, 3])
        if request.url.path == "/boom":
            return httpx.Response(500, json={"error": "server"})
        return httpx.Response(404, json={"error": "not found"})

    return handler


def call(url):
    calls = []

    async def main():
        transport = httpx.MockTransport(make_handler(calls))
        async with httpx.AsyncClient(transport=transport) as client:
            return await get_json(client, url)

    return asyncio.run(main()), calls


def test_returns_decoded_json():
    result, calls = call(BASE + "/users/1")
    assert result == {"id": 1, "name": "Asha"}, (
        f"Got {result!r}. Return response.json() (the decoded body), not the response or its text."
    )


def test_returns_any_json_value():
    result, _ = call(BASE + "/list")
    assert result == [1, 2, 3], "JSON can be a list too; just return whatever .json() decodes."


def test_sends_exactly_one_get_to_the_url():
    _, calls = call(BASE + "/users/1")
    assert calls == [("GET", BASE + "/users/1")], (
        f"The fake server saw {calls}. Send one GET to exactly the url you were given, "
        "using the client parameter."
    )


def test_404_raises_http_status_error():
    with pytest.raises(httpx.HTTPStatusError) as info:
        call(BASE + "/users/99")
    assert info.value.response.status_code == 404, (
        "The error should carry the 404 response. Call response.raise_for_status()."
    )


def test_500_raises_too():
    with pytest.raises(httpx.HTTPStatusError):
        call(BASE + "/boom")
    # httpx does not raise for bad statuses by itself: an error JSON body would be returned
    # as if it were good data unless you call raise_for_status().


def test_is_a_coroutine_function():
    import inspect

    assert inspect.iscoroutinefunction(get_json), (
        "get_json must be 'async def' so the caller can await it next to other requests."
    )
