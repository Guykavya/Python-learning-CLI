import base64
import hashlib
import hmac
import inspect

import pytest

import solution
from solution import hash_password, verify_password

FAST = 1000


def test_format():
    h = hash_password("correct horse", iterations=FAST)
    parts = h.split("$")
    assert len(parts) == 4, f"Expected 4 parts joined by '$'; got {len(parts)}: {h!r}"
    assert parts[0] == "pbkdf2_sha256", f"The first part names the scheme 'pbkdf2_sha256'; got {parts[0]!r}"
    assert parts[1] == "1000", f"The second part is the number of iterations as text; got {parts[1]!r}"
    salt = base64.b64decode(parts[2])
    digest = base64.b64decode(parts[3])
    assert len(salt) == 16, f"The salt must be 16 random bytes (os.urandom(16)); got {len(salt)} bytes"
    assert len(digest) == 32, f"pbkdf2_hmac with sha256 gives 32 bytes; got {len(digest)}"


def test_the_digest_is_really_pbkdf2():
    h = hash_password("correct horse", iterations=FAST)
    _, n, salt_b64, digest_b64 = h.split("$")
    expected = hashlib.pbkdf2_hmac("sha256", b"correct horse", base64.b64decode(salt_b64), int(n))
    assert base64.b64decode(digest_b64) == expected, (
        "The stored digest must be hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations).")


def test_verify_right_and_wrong():
    h = hash_password("correct horse", iterations=FAST)
    assert verify_password("correct horse", h) is True, "The right password must verify."
    assert verify_password("correct hors", h) is False, "A wrong password must not verify."
    assert verify_password("", h) is False


def test_same_password_gives_different_strings():
    a = hash_password("same", iterations=FAST)
    b = hash_password("same", iterations=FAST)
    assert a != b, "Two hashes of the same password must differ: use a NEW random salt on every call."
    assert verify_password("same", a) and verify_password("same", b), "Both must still verify."


def test_iterations_are_read_from_the_string():
    h = hash_password("pw", iterations=2000)
    assert verify_password("pw", h), "verify_password must use the iterations stored in the string (2000 here)."
    scheme, n, salt, digest = h.split("$")
    changed = "$".join([scheme, "1000", salt, digest])
    assert verify_password("pw", changed) is False, (
        "With the iterations changed to 1000 the digest no longer matches: verify must recompute with the stored count.")


@pytest.mark.parametrize("stored", [
    "garbage", "", "pbkdf2_sha256$1000$abc", "md5$1000$AAAA$AAAA",
    "pbkdf2_sha256$many$AAAAAAAAAAAAAAAAAAAAAA==$AAAA", "pbkdf2_sha256$1000$***$AAAA",
    "pbkdf2_sha256$1000$AAAA$AAAA$extra",
])
def test_broken_strings_are_false_not_errors(stored):
    assert verify_password("x", stored) is False, f"verify_password({stored!r}) must return False, not raise or return True."


def test_uses_compare_digest(monkeypatch):
    calls = []
    real = hmac.compare_digest

    def spy(a, b):
        calls.append(1)
        return real(a, b)

    monkeypatch.setattr(hmac, "compare_digest", spy)
    if hasattr(solution, "compare_digest"):
        monkeypatch.setattr(solution, "compare_digest", spy)
    h = hash_password("pw", iterations=FAST)
    verify_password("pw", h)
    verify_password("nope", h)
    assert len(calls) == 2, (
        "Compare digests with hmac.compare_digest (constant time), not with ==. "
        f"It was called {len(calls)} times for 2 checks.")


def test_default_is_slow_enough():
    default = inspect.signature(hash_password).parameters["iterations"].default
    assert isinstance(default, int) and default >= 600_000, (
        f"The default number of iterations must be at least 600000 (current advice for PBKDF2-SHA256); got {default!r}")
