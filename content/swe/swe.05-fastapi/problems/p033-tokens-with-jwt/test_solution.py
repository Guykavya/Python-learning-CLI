import base64
import json

import jwt
import pytest

from solution import SECRET, InvalidToken, make_token, read_token

NOW = 1_700_000_000          # a fixed moment in November 2023


def expect_invalid(token, now=NOW, why=""):
    try:
        result = read_token(token, now)
    except InvalidToken:
        return
    except Exception as exc:
        pytest.fail(f"{why}: read_token raised {type(exc).__name__} instead of InvalidToken. "
                    "Catch jwt.PyJWTError and raise InvalidToken from it.")
    pytest.fail(f"{why}: read_token accepted it and returned {result!r}; it must raise InvalidToken.")


def b64url(data):
    return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).rstrip(b"=").decode()


def test_secret_is_long_enough():
    assert len(SECRET.encode()) >= 32, "An HS256 key must be at least 32 bytes."


def test_claims():
    token = make_token(42, NOW)
    assert isinstance(token, str) and token.count(".") == 2, f"A JWT is header.payload.signature; got {token!r}"
    assert jwt.get_unverified_header(token)["alg"] == "HS256", "Sign with algorithm='HS256'."
    payload = jwt.decode(token, options={"verify_signature": False})
    assert payload.get("sub") == "42", f"sub must be the user id as a STRING ('42'); got {payload.get('sub')!r}"
    assert payload.get("exp") == NOW + 900, f"exp = now + 15 * 60 = {NOW + 900}; got {payload.get('exp')!r}. Use the given now, not time.time()."


def test_minutes():
    payload = jwt.decode(make_token(1, NOW, minutes=1), options={"verify_signature": False})
    assert payload["exp"] == NOW + 60, f"minutes=1 gives exp = now + 60; got {payload['exp'] - NOW} seconds"


def test_round_trip_with_the_injected_clock():
    token = make_token(42, NOW)
    try:
        got = read_token(token, NOW)
    except Exception as exc:
        pytest.fail(f"A fresh token was refused ({type(exc).__name__}: {exc}). NOW is in 2023, so if PyJWT checks exp "
                    "against the real clock every token looks expired: pass options={'verify_exp': False} and "
                    "compare exp with the given now yourself.")
    assert got == 42 and isinstance(got, int), f"read_token returns the user id as an int; got {got!r}"
    assert read_token(token, NOW + 899) == 42, "One second before exp the token is still valid."


def test_expired():
    expect_invalid(make_token(42, NOW), NOW + 900, "At now == exp the token has expired")
    expect_invalid(make_token(42, NOW), NOW + 10_000, "Long after exp")


def test_wrong_key():
    forged = jwt.encode({"sub": "42", "exp": NOW + 900}, "another-key-" + "x" * 40, algorithm="HS256")
    expect_invalid(forged, why="A token signed with another key")


def test_alg_none():
    unsigned = jwt.encode({"sub": "1", "exp": NOW + 900}, None, algorithm="none")
    expect_invalid(unsigned, why="An 'alg: none' token has no signature")


def test_tampered_payload():
    header, payload, signature = make_token(42, NOW).split(".")
    evil = ".".join([header, b64url({"sub": "1", "exp": NOW + 900}), signature])
    expect_invalid(evil, why="The payload was changed to sub '1' but the signature was kept")


def test_tampered_signature():
    token = make_token(42, NOW)
    flipped = token[:-3] + ("AAA" if not token.endswith("AAA") else "BBB")
    expect_invalid(flipped, why="The signature was changed")


@pytest.mark.parametrize("bad", ["abc", "", "a.b.c"])
def test_not_a_token(bad):
    expect_invalid(bad, why=f"{bad!r} is not a JWT")


def test_missing_claims():
    expect_invalid(jwt.encode({"sub": "42"}, SECRET, algorithm="HS256"), why="A token without exp")
    expect_invalid(jwt.encode({"exp": NOW + 900}, SECRET, algorithm="HS256"), why="A token without sub")


def test_non_numeric_subject():
    expect_invalid(jwt.encode({"sub": "asha", "exp": NOW + 900}, SECRET, algorithm="HS256"),
                   why="sub 'asha' is not a user id number")
