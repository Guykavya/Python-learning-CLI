import pytest

from solution import build_response


def test_exact_bytes_of_a_simple_response():
    assert build_response(200, "hi") == (
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 2\r\n\r\nhi")


def test_reason_phrases():
    assert build_response(404, "x").startswith(b"HTTP/1.1 404 Not Found\r\n")
    assert build_response(201, "x").startswith(b"HTTP/1.1 201 Created\r\n")
    assert build_response(418, "x").startswith(b"HTTP/1.1 418 I'm a Teapot\r\n")
    assert build_response(799, "x").startswith(b"HTTP/1.1 799 Unknown\r\n"), "An unknown code gets the phrase 'Unknown'."


def test_content_length_counts_bytes_not_characters():
    out = build_response(200, "é")
    assert b"Content-Length: 2\r\n" in out, "'é' is 2 bytes in UTF-8: Content-Length must count bytes, not characters."
    assert out.endswith("é".encode("utf-8"))
    emoji = build_response(200, "😀")
    assert b"Content-Length: 4\r\n" in emoji


def test_bytes_body_and_content_type():
    out = build_response(200, b"\x00\x01\x02", "application/octet-stream")
    assert out == (b"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: 3\r\n\r\n\x00\x01\x02")


def test_empty_body_has_zero_length():
    out = build_response(200)
    assert out.endswith(b"Content-Length: 0\r\n\r\n"), "No body: Content-Length: 0 and nothing after the blank line."


def test_line_endings_are_crlf():
    head = build_response(200, "x").split(b"\r\n\r\n", 1)[0]
    assert b"\n" not in head.replace(b"\r\n", b""), "Every header line must end with \\r\\n."


@pytest.mark.parametrize("status", [204, 304, 101])
def test_no_body_statuses(status):
    out = build_response(status)
    assert b"Content-Length" not in out and b"Content-Type" not in out, (
        f"A {status} response has no body: no Content-Length and no Content-Type.")
    assert out.endswith(b"\r\n\r\n") and out.count(b"\r\n") == 2


def test_body_with_204_is_an_error():
    with pytest.raises(ValueError):
        build_response(204, "oops")
