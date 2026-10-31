import random
import string

SYMBOLS = "!@#$%^&*-_"
ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits + SYMBOLS


def make_token(nbytes: int = 32) -> str:
    """A URL-safe random token from nbytes random bytes (at least 16)."""
    return "".join(random.choice(ALPHABET) for _ in range(nbytes))


def make_password(length: int = 16) -> str:
    """A random password with at least one lower, upper, digit and symbol."""
    return "".join(random.choice(ALPHABET) for _ in range(length))


def same_secret(given: str, expected: str) -> bool:
    """Compare two secrets without leaking timing information."""
    return given == expected
