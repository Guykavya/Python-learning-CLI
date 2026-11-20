import httpx
import pytest

from solution import ApiError, raise_for_api


def test_success_returns_the_response():
    r = httpx.Response(200, json={"ok": True})
    assert raise_for_api(r) is r
    r = httpx.Response(302, headers={"Location": "/x"})
    assert raise_for_api(r) is r, "Only 400 and above are errors."


def test_json_error_body():
    r = httpx.Response(404, json={"error": {"code": "no-book", "message": "No book 7"}})
    with pytest.raises(ApiError) as e:
        raise_for_api(r)
    err = e.value
    assert (err.status, err.code, err.message) == (404, "no-book", "No book 7")
    assert str(err) == "404 no-book: No book 7"


def test_html_proxy_page_falls_back_on_the_status():
    r = httpx.Response(502, text="<html><h1>Bad Gateway</h1></html>", headers={"Content-Type": "text/html"})
    with pytest.raises(ApiError) as e:
        raise_for_api(r)
    assert (e.value.status, e.value.code, e.value.message) == (502, "bad-gateway", "Bad Gateway"), (
        "An HTML body is not JSON: use the fallback (code from the status, message from the reason phrase).")


@pytest.mark.parametrize("status,code,message", [
    (400, "bad-request", "Bad Request"), (401, "unauthorized", "Unauthorized"), (403, "forbidden", "Forbidden"),
    (404, "not-found", "Not Found"), (409, "conflict", "Conflict"), (422, "unprocessable", "Unprocessable Content"),
    (429, "too-many-requests", "Too Many Requests"), (500, "internal-error", "Internal Server Error"),
    (503, "service-unavailable", "Service Unavailable"), (504, "gateway-timeout", "Gateway Timeout"),
    (418, "http-418", "I'm a Teapot"), (599, "http-599", "HTTP 599"),
])
def test_fallback_codes_and_messages(status, code, message):
    with pytest.raises(ApiError) as e:
        raise_for_api(httpx.Response(status, content=b""))
    got = (e.value.code, e.value.message)
    if status == 422:   # the phrase differs between Python versions
        assert got[0] == code
    else:
        assert got == (code, message), f"Status {status}: expected {(code, message)}, got {got}."


def test_partial_json_error():
    with pytest.raises(ApiError) as e:
        raise_for_api(httpx.Response(409, json={"error": {"message": "Version conflict"}}))
    assert (e.value.code, e.value.message) == ("conflict", "Version conflict"), "A missing code falls back to the status code."
    with pytest.raises(ApiError) as e:
        raise_for_api(httpx.Response(400, json={"error": {"code": "bad-date"}}))
    assert (e.value.code, e.value.message) == ("bad-date", "Bad Request")


def test_string_error_and_detail():
    with pytest.raises(ApiError) as e:
        raise_for_api(httpx.Response(403, json={"error": "not allowed"}))
    assert (e.value.code, e.value.message) == ("forbidden", "not allowed")
    with pytest.raises(ApiError) as e:
        raise_for_api(httpx.Response(404, json={"detail": "Item not found"}))
    assert e.value.message == "Item not found"


def test_json_of_the_wrong_shape():
    for body in ([1, 2, 3], "text", 42, None, {"error": None}, {"error": 5}):
        with pytest.raises(ApiError) as e:
            raise_for_api(httpx.Response(500, json=body))
        assert e.value.status == 500 and e.value.code == "internal-error", f"Body {body!r}: use the fallback."


def test_api_error_is_an_exception_with_attributes():
    err = ApiError(418, "teapot", "short and stout")
    assert isinstance(err, Exception) and (err.status, err.code, err.message) == (418, "teapot", "short and stout")
    assert str(err) == "418 teapot: short and stout"
