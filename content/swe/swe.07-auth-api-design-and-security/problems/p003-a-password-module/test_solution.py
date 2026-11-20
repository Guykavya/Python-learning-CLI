import base64
import hmac

import pytest

from solution import N, hash_password, verify_password

SMALL = dict(n=2**10, r=8, p=1)          # cheap on purpose: the tests hash many times


def test_default_cost_is_not_tiny():
    assert N >= 2**14, f"The default N must be at least 2**14 (16384); it is {N}. A cheap hash is fast for the attacker too."


def test_format_is_self_describing():
    stored = hash_password("correct horse battery", **SMALL)
    assert isinstance(stored, str), f"hash_password must return a str; got {type(stored).__name__}"
    parts = stored.split("$")
    assert len(parts) == 6, f"Expected 6 parts joined by '$' (scheme, n, r, p, salt, digest); got {len(parts)}: {stored!r}"
    assert parts[:4] == ["scrypt", "1024", "8", "1"], f"The first four parts must be scrypt, n, r, p as given; got {parts[:4]}"


def test_salt_is_16_random_bytes():
    parts = hash_password("pw", **SMALL).split("$")
    try:
        salt = base64.b64decode(parts[4], validate=True)
    except Exception:
        pytest.fail("The salt part must be valid standard base64 (base64.b64encode).")
    assert len(salt) == 16, f"The salt must be 16 bytes (os.urandom(16)); got {len(salt)}"
    digest = base64.b64decode(parts[5], validate=True)
    assert len(digest) == 64, f"scrypt's default output is 64 bytes; got {len(digest)}. Do not pass dklen."


def test_same_password_gives_different_strings():
    a = hash_password("same-password", **SMALL)
    b = hash_password("same-password", **SMALL)
    assert a != b, "Two hashes of one password must differ: use a NEW random salt on every call, never a fixed one."


def test_right_and_wrong_password():
    stored = hash_password("correct horse battery", **SMALL)
    assert verify_password("correct horse battery", stored) is True, "The right password must verify (True)."
    assert verify_password("wrong", stored) is False, "A wrong password must give False."
    assert verify_password("Correct horse battery", stored) is False, "Passwords are case sensitive."
    assert verify_password("", stored) is False, "The empty password is wrong, not an error."


def test_parameters_come_from_the_string():
    old = hash_password("old-password", n=2**9, r=8, p=1)
    assert verify_password("old-password", old) is True, \
        "A hash made with n=2**9 must verify: read n, r, p from the stored string, not from the constants N, R, P."
    other = hash_password("pw", n=2**10, r=4, p=2)
    assert verify_password("pw", other) is True, "r and p also come from the string."


def test_unicode_password():
    pw = "pässwörd-日本語-🔑"
    stored = hash_password(pw, **SMALL)
    assert verify_password(pw, stored) is True, "Encode the password as UTF-8 (password.encode()) so any text works."
    assert verify_password("passwörd-日本語-🔑", stored) is False, "A different unicode password must not verify."


@pytest.mark.parametrize("bad", [
    "", "garbage", "scrypt", "scrypt$1024$8$1$abc",
    "scrypt$x$8$1$AAAA$AAAA",
    "scrypt$1024$8$1$@@@@$AAAA",
    "scrypt$1024$8$1$AAAA$@@@@",
    "scrypt$1024$8$1$AAAA$AAAA$extra",
    "scrypt$0$8$1$AAAA$AAAA",
    "scrypt$1000$8$1$AAAA$AAAA",        # n is not a power of two
])
def test_garbage_is_false_not_an_exception(bad):
    try:
        result = verify_password("pw", bad)
    except Exception as exc:
        pytest.fail(f"verify_password raised {type(exc).__name__} for {bad!r}; return False for any string that is not a valid hash.")
    assert result is False, f"{bad!r} is not a valid stored hash: expected False, got {result!r}"


def test_wrong_scheme_is_false():
    stored = hash_password("pw", **SMALL)
    forged = "bcrypt" + stored[len("scrypt"):]
    assert verify_password("pw", forged) is False, "Only the scheme 'scrypt' is understood; any other name must give False."


def test_tampered_digest_is_false():
    parts = hash_password("pw", **SMALL).split("$")
    digest = bytearray(base64.b64decode(parts[5]))
    digest[0] ^= 1
    parts[5] = base64.b64encode(bytes(digest)).decode()
    assert verify_password("pw", "$".join(parts)) is False, "A changed digest must not verify."


def test_uses_constant_time_comparison(monkeypatch):
    calls = []
    real = hmac.compare_digest

    def spy(a, b):
        calls.append((type(a), type(b)))
        return real(a, b)

    monkeypatch.setattr(hmac, "compare_digest", spy)
    stored = hash_password("pw", **SMALL)
    assert verify_password("pw", stored) is True
    assert calls, "verify_password must compare the digests with hmac.compare_digest (call it as hmac.compare_digest), not with ==."
