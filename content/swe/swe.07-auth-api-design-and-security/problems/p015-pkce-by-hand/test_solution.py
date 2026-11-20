import base64
import hashlib
import re

import pytest

from solution import challenge_for, make_verifier

RFC_VERIFIER = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
RFC_CHALLENGE = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


def test_rfc_7636_appendix_b_vector():
    got = challenge_for(RFC_VERIFIER)
    assert got == RFC_CHALLENGE, (
        f"Wrong challenge {got!r}. S256 means base64url(SHA-256(verifier)) with the '=' padding removed; "
        "hash the verifier text (ASCII bytes), not its hex digest.")


def test_verifier_length_and_alphabet():
    for _ in range(50):
        v = make_verifier()
        assert 43 <= len(v) <= 128, f"A verifier has 43 to 128 characters, yours has {len(v)}."
        assert re.fullmatch(r"[A-Za-z0-9\-._~]+", v), f"Illegal character in the verifier {v!r}; allowed: A-Z a-z 0-9 - . _ ~"


def test_verifiers_are_unique():
    assert len({make_verifier() for _ in range(200)}) == 200, "Verifiers repeat: use secrets (random bytes), never a counter or the time."


def test_challenge_is_43_chars_without_padding():
    c = challenge_for(make_verifier())
    assert len(c) == 43 and "=" not in c, f"A SHA-256 digest in base64url without padding has 43 characters and no '=': got {c!r}."
    assert "+" not in c and "/" not in c, "Use the URL-safe alphabet (- and _), not + and /."


def test_challenge_is_deterministic_and_matches_hashlib():
    v = "a" * 43
    expected = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
    assert challenge_for(v) == challenge_for(v) == expected, "The same verifier must always give the same challenge."


def test_different_verifiers_give_different_challenges():
    assert challenge_for("a" * 43) != challenge_for("b" * 43)


@pytest.mark.parametrize("bad", ["", "short", "a" * 42, "a" * 129, "a" * 42 + " ", "a" * 42 + "+", "a" * 42 + "é"])
def test_invalid_verifiers_are_refused(bad):
    with pytest.raises(ValueError):
        challenge_for(bad)


def test_boundary_lengths_are_accepted():
    assert challenge_for("a" * 43) and challenge_for("a" * 128), "43 and 128 characters are both legal lengths."
