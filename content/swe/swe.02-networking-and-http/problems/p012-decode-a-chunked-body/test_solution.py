import pytest

from solution import decode_chunked


def test_the_classic_example():
    assert decode_chunked(b"4\r\nWiki\r\n5\r\npedia\r\n0\r\n\r\n") == (b"Wikipedia", {})


def test_hex_sizes():
    body = b"0123456789abcdefXYZ"          # 19 bytes = 0x13
    assert decode_chunked(b"13\r\n" + body + b"\r\n0\r\n\r\n")[0] == body, "Sizes are hexadecimal: 13 means 19."
    assert decode_chunked(b"A\r\n0123456789\r\n0\r\n\r\n")[0] == b"0123456789"
    assert decode_chunked(b"a\r\n0123456789\r\n0\r\n\r\n")[0] == b"0123456789", "Upper and lower case hex both work."


def test_extensions_are_ignored():
    assert decode_chunked(b"4;x=1\r\nWiki\r\n0;done\r\n\r\n")[0] == b"Wiki"


def test_trailers():
    body, trailers = decode_chunked(b"3\r\nabc\r\n0\r\nX-Checksum: 99\r\nExpires:  never \r\n\r\n")
    assert body == b"abc"
    assert trailers == {"x-checksum": "99", "expires": "never"}, "Trailer names are lower-case, values stripped."


def test_empty_body():
    assert decode_chunked(b"0\r\n\r\n") == (b"", {})


def test_chunk_data_may_contain_crlf():
    assert decode_chunked(b"9\r\nab\r\n0\r\n\r\n\r\n0\r\n\r\n") == (b"ab\r\n0\r\n\r\n", {}), (
        "The size decides where the chunk ends; the data may contain \\r\\n and even '0\\r\\n\\r\\n'.")


def test_binary_data():
    data = bytes(range(256))
    assert decode_chunked(b"100\r\n" + data + b"\r\n0\r\n\r\n")[0] == data


@pytest.mark.parametrize("raw", [
    b"zz\r\nab\r\n0\r\n\r\n",
    b"0x4\r\nWiki\r\n0\r\n\r\n",
    b"+4\r\nWiki\r\n0\r\n\r\n",
    b"-1\r\nWiki\r\n0\r\n\r\n",
    b"\r\nWiki\r\n0\r\n\r\n",
    b"5\r\nab\r\n0\r\n\r\n",            # chunk shorter than its size
    b"4\r\nWikiXX0\r\n\r\n",            # no CRLF after the data
    b"4\r\nWiki\r\n",                   # no final 0 chunk
    b"4\r\nWiki\r\n0\r\n",              # no final blank line
    b"4\r\nWiki\r\n0\r\nNoColonHere\r\n\r\n",
    b"4\r\nWiki",                       # cut inside
    b"",
])
def test_malformed_input(raw):
    with pytest.raises(ValueError):
        decode_chunked(raw)
