import base64
import hashlib
import hmac
import os


def hash_password(password: str, iterations: int = 600_000) -> str:
    """Return 'pbkdf2_sha256$<iterations>$<salt b64>$<digest b64>'."""
    return ""


def verify_password(password: str, stored: str) -> bool:
    """True if password matches the stored string; False for a wrong password or a broken string."""
    return False
