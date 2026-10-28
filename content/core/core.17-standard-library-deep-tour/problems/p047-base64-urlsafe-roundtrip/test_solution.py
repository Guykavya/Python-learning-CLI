import base64

import pytest

from solution import decode_text, decode_token, encode_text, encode_token


def test_encode_urlsafe_alphabet():
    assert encode_token(b"\xfb\xff\xbf") == "-_-_", "Use urlsafe_b64encode: '-' and '_' instead of '+' and '/'."
    assert encode_token(b"\xfb\xef") == "--8", "Standard Base64 here is '++8=': URL-safe and without padding it is '--8'."


def test_encode_returns_str_without_padding():
    token = encode_token(b"hi")
    assert isinstance(token, str), "Return a str: the base64 functions return bytes, so .decode('ascii') the result."
    assert token == "aGk", "b'hi' is 'aGk=' in Base64; remove the trailing '=' padding."
    assert encode_token(b"hi!") == "aGkh", "3 bytes need no padding: 'aGkh'."
    assert encode_token(b"") == "", "Empty bytes give an empty token."


def test_roundtrip_all_lengths():
    for n in range(0, 20):
        data = bytes((i * 37 + 250) % 256 for i in range(n))
        token = encode_token(data)
        assert "=" not in token and "+" not in token and "/" not in token, f"Token for {n} bytes contains '=', '+' or '/'."
        assert decode_token(token) == data, (
            f"decode_token(encode_token(data)) must give the data back ({n} bytes). Re-add '=' until len % 4 == 0."
        )


def test_decode_accepts_padding():
    assert decode_token("aGk") == b"hi", "Put back the missing padding: 'aGk' + '=' has length 4."
    assert decode_token("aGk=") == b"hi", "A token that still has its padding must also work."
    assert decode_token("aA") == b"h", "'aA' needs two '=' to reach a multiple of 4."


@pytest.mark.parametrize("bad", ["aG+k", "aG/k", "aG k", "aG.k", "a=Gk", "aGk!"])
def test_decode_rejects_bad_characters(bad):
    with pytest.raises(ValueError):
        decode_token(bad)


def test_decode_rejects_impossible_length():
    with pytest.raises(ValueError):
        decode_token("aGkha")   # 5 characters: one more than a multiple of 4 can never be valid


def test_bad_characters_are_not_ignored():
    # urlsafe_b64decode would quietly accept these; the token must be refused instead
    assert base64.urlsafe_b64decode("aG+k") == b"ho\xa4", "Python check: the library decoder accepts '+' without complaint."
    with pytest.raises(ValueError):
        decode_token("aG+k")


def test_text_roundtrip():
    assert encode_text("café") == "Y2Fmw6k", "Encode the text to UTF-8 bytes first, then encode_token."
    assert decode_text("Y2Fmw6k") == "café", "decode_token then .decode('utf-8')."
    assert decode_text(encode_text("नमस्ते 👋")) == "नमस्ते 👋", "Any Unicode text must survive the round trip."
