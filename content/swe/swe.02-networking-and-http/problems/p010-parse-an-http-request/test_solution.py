import pytest

from solution import BadRequest, parse_request

OK = b"POST /notes?x=1 HTTP/1.1\r\nHost: example.com\r\nContent-Type: application/json\r\nContent-Length: 5\r\n\r\nhello"


def test_a_normal_request():
    r = parse_request(OK)
    assert (r.method, r.target, r.version) == ("POST", "/notes?x=1", "HTTP/1.1")
    assert r.body == b"hello"
    assert r.headers.get("Content-Type") == "application/json"


def test_header_names_are_case_insensitive():
    r = parse_request(OK)
    assert r.headers.get("HOST") == "example.com" and r.headers.get("host") == "example.com", "Header names ignore case."
    assert "content-length" in r.headers and "X-Nope" not in r.headers
    assert r.headers.get("X-Nope") is None and r.headers.get("X-Nope", "d") == "d"


def test_repeated_headers_are_kept():
    raw = b"GET / HTTP/1.1\r\nHost: x\r\nAccept: text/html\r\nAccept: application/json\r\n\r\n"
    r = parse_request(raw)
    assert r.headers.get_all("accept") == ["text/html", "application/json"], "Keep every copy, in order."
    assert r.headers.get("accept") == "text/html", "get returns the first value."
    assert [k for k, _ in r.headers.items()] == ["Host", "Accept", "Accept"]


def test_values_are_stripped_names_kept_as_sent():
    r = parse_request(b"GET / HTTP/1.1\r\nHost:   x.org  \r\n\r\n")
    assert r.headers.get("host") == "x.org"
    assert r.headers.items() == [("Host", "x.org")]


def test_no_body_and_extra_bytes_after_the_body():
    assert parse_request(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n").body == b""
    r = parse_request(b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: 3\r\n\r\nabcGET /next")
    assert r.body == b"abc", "Take exactly Content-Length bytes; the rest belongs to the next request."


def test_body_may_contain_a_blank_line_and_any_bytes():
    body = b"a\r\n\r\nb\xff\x00"
    r = parse_request(b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
    assert r.body == body, "Cut at the FIRST blank line; the body is counted, not searched, and is raw bytes."


def test_http_10_needs_no_host():
    r = parse_request(b"GET / HTTP/1.0\r\n\r\n")
    assert r.version == "HTTP/1.0"


@pytest.mark.parametrize("raw", [
    b"GET /\r\nHost: x\r\n\r\n",
    b"GET / HTTP/1.1 extra\r\nHost: x\r\n\r\n",
    b"GET / FTP/1.1\r\nHost: x\r\n\r\n",
    b"GET  / HTTP/1.1\r\nHost: x\r\n\r\n",
    b"\r\n\r\n",
])
def test_bad_request_line(raw):
    with pytest.raises(BadRequest):
        parse_request(raw)


@pytest.mark.parametrize("raw", [
    b"GET / HTTP/1.1\r\n\r\n",                                   # no Host on 1.1
    b"GET / HTTP/1.1\r\nHost: x\r\nBroken line\r\n\r\n",          # no colon
    b"GET / HTTP/1.1\r\nHost : x\r\n\r\n",                        # space before the colon
    b"GET / HTTP/1.1\r\n: x\r\n\r\n",                             # empty name
    b"GET / HTTP/1.1\r\nHost: x\r\n",                             # no blank line
    b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: abc\r\n\r\n",
    b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: -1\r\n\r\n",
    b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: 5\r\n\r\nhi",     # body cut short
    b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: 2\r\nContent-Length: 3\r\n\r\nabc",
])
def test_bad_requests(raw):
    with pytest.raises(BadRequest):
        parse_request(raw)


def test_same_content_length_twice_is_allowed():
    r = parse_request(b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: 2\r\nContent-Length: 2\r\n\r\nab")
    assert r.body == b"ab"
