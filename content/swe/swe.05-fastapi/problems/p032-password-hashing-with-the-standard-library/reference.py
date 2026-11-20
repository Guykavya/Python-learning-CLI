import base64
import hashlib
import hmac
import os

SCHEME = "pbkdf2_sha256"


def hash_password(password: str, iterations: int = 600_000) -> str:
    """Return 'pbkdf2_sha256$<iterations>$<salt b64>$<digest b64>'."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    parts = [SCHEME, str(iterations), base64.b64encode(salt).decode(), base64.b64encode(digest).decode()]
    return "$".join(parts)


def verify_password(password: str, stored: str) -> bool:
    """True if password matches the stored string; False for a wrong password or a broken string."""
    try:
        scheme, iterations_text, salt_b64, digest_b64 = stored.split("$")
        iterations = int(iterations_text)
        salt = base64.b64decode(salt_b64, validate=True)
        expected = base64.b64decode(digest_b64, validate=True)
    except ValueError:                       # wrong number of parts, not a number, bad base64
        return False
    if scheme != SCHEME or iterations < 1:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return hmac.compare_digest(actual, expected)
