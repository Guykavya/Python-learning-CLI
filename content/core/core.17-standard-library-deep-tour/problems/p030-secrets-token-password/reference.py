import secrets
import string

SYMBOLS = "!@#$%^&*-_"
ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits + SYMBOLS


def make_token(nbytes: int = 32) -> str:
    if nbytes < 16:
        raise ValueError("use at least 16 random bytes for a token")
    return secrets.token_urlsafe(nbytes)


def make_password(length: int = 16) -> str:
    if length < 8:
        raise ValueError("a password needs at least 8 characters")
    chars = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(SYMBOLS),
    ]
    chars += [secrets.choice(ALPHABET) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def same_secret(given: str, expected: str) -> bool:
    return secrets.compare_digest(given.encode("utf-8"), expected.encode("utf-8"))
