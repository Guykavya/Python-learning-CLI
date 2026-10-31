import inspect
import string

import pytest

import solution
from solution import make_password, make_token, same_secret

SYMBOLS = "!@#$%^&*-_"
URLSAFE = set(string.ascii_letters + string.digits + "-_")
ALLOWED = set(string.ascii_letters + string.digits + SYMBOLS)


# Secrets cannot be checked by value (they are unpredictable on purpose), so every test below
# checks PROPERTIES: length, alphabet, uniqueness, and the source of randomness.


def test_does_not_use_the_random_module():
    assert not hasattr(solution, "random"), (
        "solution.py imports the random module. random is predictable (Mersenne Twister) and must never be used "
        "for tokens or passwords. Use the secrets module."
    )


def test_token_alphabet_and_length():
    tok = make_token()
    assert isinstance(tok, str), "make_token returns a str."
    assert set(tok) <= URLSAFE, "Use secrets.token_urlsafe: only letters, digits, '-' and '_' (safe inside a URL)."
    assert len(tok) == 43, "token_urlsafe(32) gives 43 characters (32 bytes in base64, without '=' padding)."
    assert len(make_token(16)) == 22, "16 random bytes give 22 URL-safe characters."


def test_tokens_are_unique():
    tokens = {make_token() for _ in range(300)}
    assert len(tokens) == 300, "Every token must be different: 32 random bytes never repeat in practice."


def test_token_too_short():
    with pytest.raises(ValueError):
        make_token(8)


def test_password_length_and_alphabet():
    for length in (8, 12, 30):
        pw = make_password(length)
        assert len(pw) == length, f"make_password({length}) must have exactly {length} characters."
        assert set(pw) <= ALLOWED, "Only lowercase, uppercase, digits and the symbols !@#$%^&*-_ are allowed."
    assert len(make_password()) == 16, "The default length is 16."


def test_password_has_every_class_every_time():
    for _ in range(500):
        pw = make_password(8)
        assert any(c in string.ascii_lowercase for c in pw), f"{pw!r} has no lowercase letter. Pick one of each class first."
        assert any(c in string.ascii_uppercase for c in pw), f"{pw!r} has no uppercase letter."
        assert any(c in string.digits for c in pw), f"{pw!r} has no digit."
        assert any(c in SYMBOLS for c in pw), (
            f"{pw!r} has no symbol. Choosing 8 characters from the whole alphabet misses a class about 3 times in 10."
        )


def test_password_positions_are_shuffled():
    firsts = {make_password(8)[0] for _ in range(200)}
    kinds = {
        "lower" if c in string.ascii_lowercase else "upper" if c in string.ascii_uppercase
        else "digit" if c in string.digits else "symbol"
        for c in firsts
    }
    assert len(kinds) >= 3, (
        "The first character is always the same kind. After picking one of each class, shuffle the list "
        "(secrets.SystemRandom().shuffle) so the positions do not reveal anything."
    )


def test_passwords_are_unique():
    assert len({make_password() for _ in range(300)}) == 300, "Passwords must not repeat."


def test_password_too_short():
    with pytest.raises(ValueError):
        make_password(7)


def test_same_secret_results():
    assert same_secret("s3cret-token", "s3cret-token") is True, "Equal secrets give True."
    assert same_secret("s3cret-token", "s3cret-tokeN") is False, "One different character gives False."
    assert same_secret("short", "much longer value") is False, "Different lengths give False."
    assert same_secret("", "") is True, "Two empty strings are equal."
    assert same_secret("café", "café") is True, "Non-ASCII text must work: encode to bytes first."


def test_same_secret_uses_compare_digest():
    src = inspect.getsource(same_secret)
    assert "compare_digest" in src, (
        "Compare secrets with secrets.compare_digest (or hmac.compare_digest). '==' stops at the first different "
        "character, so the time it takes leaks how much of a guess was right."
    )
