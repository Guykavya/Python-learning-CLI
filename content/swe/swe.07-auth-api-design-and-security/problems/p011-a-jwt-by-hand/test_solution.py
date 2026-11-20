import base64
import hashlib
import hmac
import json
import warnings

import jwt
import pytest

from solution import InvalidToken, sign, verify

KEY = b"a-long-random-demo-key-of-at-least-32-bytes!"
OTHER = b"another-long-random-key-of-32-bytes-or-more"
PAYLOAD = {"sub": "42", "role": "member", "exp": 2_000_000_000}
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64u_json(data):
    return b64u(json.dumps(data, separators=(",", ":")).encode())


def forge(header, payload, key=KEY):
    """A correctly signed token with any header and payload (made independently of the solution)."""
    signing_input = b64u_json(header) + "." + b64u_json(payload)
    return signing_input + "." + b64u(hmac.new(key, signing_input.encode(), hashlib.sha256).digest())


def reject(token, why, key=KEY):
    try:
        result = verify(token, key)
    except InvalidToken:
        return
    except Exception as exc:
        pytest.fail(f"{why}: verify raised {type(exc).__name__} instead of InvalidToken. Turn every problem into InvalidToken.")
    pytest.fail(f"{why}: verify accepted the token and returned {result!r}; it must raise InvalidToken.")


def test_sign_shape():
    token = sign(PAYLOAD, KEY)
    assert isinstance(token, str) and token.count(".") == 2, f"A JWT is header.payload.signature (two dots); got {token!r}"
    assert "=" not in token, "base64url without padding: strip the '=' characters."
    assert "+" not in token and "/" not in token, "Use the URL-safe alphabet ('-' and '_'), not '+' and '/'."


def test_header_and_payload_are_what_the_chapter_shows():
    head, body, _ = sign(PAYLOAD, KEY).split(".")
    pad = lambda s: s + "=" * (-len(s) % 4)           # noqa: E731
    assert json.loads(base64.urlsafe_b64decode(pad(head))) == {"alg": "HS256", "typ": "JWT"}, "The header is {'alg': 'HS256', 'typ': 'JWT'}."
    assert json.loads(base64.urlsafe_b64decode(pad(body))) == PAYLOAD, "The second part is the payload as JSON: anyone can read it (it is not encrypted)."
    assert base64.urlsafe_b64decode(pad(head)) == b'{"alg":"HS256","typ":"JWT"}', "Use json.dumps(..., separators=(',', ':')) with no spaces."


def test_signature_is_hmac_sha256_of_the_first_two_parts():
    token = sign(PAYLOAD, KEY)
    head, body, sig = token.split(".")
    expected = b64u(hmac.new(KEY, f"{head}.{body}".encode(), hashlib.sha256).digest())
    assert sig == expected, "The signature is HMAC-SHA256(key, 'header.payload'), base64url encoded without padding."


def test_pyjwt_reads_our_token():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        got = jwt.decode(sign(PAYLOAD, KEY), KEY, algorithms=["HS256"], options={"verify_exp": False})
    assert got == PAYLOAD, "A standard library must be able to read the token you made."


def test_we_read_pyjwts_token():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        theirs = jwt.encode(PAYLOAD, KEY, algorithm="HS256")
    assert verify(theirs, KEY) == PAYLOAD, "A token made by PyJWT (HS256) must verify with your verify()."


def test_round_trip():
    assert verify(sign(PAYLOAD, KEY), KEY) == PAYLOAD, "verify(sign(x)) must give x back."
    unicode_payload = {"sub": "ß-日本-🔑", "n": 1}
    assert verify(sign(unicode_payload, KEY), KEY) == unicode_payload, "Non-ASCII text must survive (encode JSON as UTF-8)."


def test_wrong_key():
    reject(sign(PAYLOAD, KEY), "Verifying with another key", key=OTHER)


def test_changed_payload():
    head, body, sig = sign(PAYLOAD, KEY).split(".")
    evil = b64u_json({**PAYLOAD, "role": "admin"})
    reject(f"{head}.{evil}.{sig}", "A changed payload with the old signature")


def test_changed_header():
    head, body, sig = sign(PAYLOAD, KEY).split(".")
    new_head = b64u_json({"alg": "HS256", "typ": "JWT", "kid": "x"})
    reject(f"{new_head}.{body}.{sig}", "A changed header with the old signature")


def test_changed_signature():
    head, body, sig = sign(PAYLOAD, KEY).split(".")
    reject(f"{head}.{body}.{'A' * len(sig)}", "A different signature")
    reject(f"{head}.{body}.", "An empty signature")


@pytest.mark.parametrize("token", ["", "abc", "a.b", "a.b.c.d", "...", "a..c"])
def test_wrong_number_of_parts_or_garbage(token):
    reject(token, f"{token!r}")


def test_alg_none_is_refused():
    token = b64u_json({"alg": "none", "typ": "JWT"}) + "." + b64u_json({"sub": "1", "role": "admin"}) + "."
    reject(token, "An 'alg: none' token with an empty signature (chapter 4.3, attack 1)")


def test_other_algorithm_with_a_valid_hmac_is_refused():
    token = forge({"alg": "HS512", "typ": "JWT"}, PAYLOAD)
    reject(token, "A header that says HS512 but was signed with HS256: the server decides the algorithm, the token does not")
    reject(forge({"typ": "JWT"}, PAYLOAD), "A header with no 'alg'")
    reject(forge({"alg": "hs256", "typ": "JWT"}, PAYLOAD), "alg must be exactly 'HS256'")


def test_correctly_signed_but_not_json_object():
    reject(forge({"alg": "HS256"}, [1, 2, 3]), "A payload that is a JSON list, not an object")
    signing_input = b64u_json({"alg": "HS256"}) + "." + b64u(b"not json at all")
    sig = b64u(hmac.new(KEY, signing_input.encode(), hashlib.sha256).digest())
    reject(signing_input + "." + sig, "A correctly signed payload that is not JSON")


def test_bad_characters():
    head, body, sig = sign(PAYLOAD, KEY).split(".")
    reject(f"{head}.{body}.{sig}!!!", "Extra characters after the signature")
    reject(f"{head}.{body}é.{sig}", "Non-ASCII text in the token must be InvalidToken, not UnicodeEncodeError")


def test_non_canonical_signature_text_is_refused():
    head, body, sig = sign(PAYLOAD, KEY).split(".")
    last = ALPHABET.index(sig[-1])
    twin = sig[:-1] + ALPHABET[last ^ 1]          # the last character holds 2 unused bits: this decodes to the SAME bytes
    assert twin != sig
    reject(f"{head}.{body}.{twin}", "The same signature bytes written with another last character. Compare the ENCODED text of the signature, not the decoded bytes")


def test_uses_constant_time_comparison(monkeypatch):
    calls = []
    real = hmac.compare_digest

    def spy(a, b):
        calls.append(1)
        return real(a, b)

    monkeypatch.setattr(hmac, "compare_digest", spy)
    verify(sign(PAYLOAD, KEY), KEY)
    assert calls, "Compare the signatures with hmac.compare_digest (called as hmac.compare_digest), not with ==."


def test_exp_is_not_checked_here():
    expired = {"sub": "1", "exp": 1}
    assert verify(sign(expired, KEY), KEY) == expired, "verify() only checks the signature and the algorithm; claims such as exp come in the next problem."
