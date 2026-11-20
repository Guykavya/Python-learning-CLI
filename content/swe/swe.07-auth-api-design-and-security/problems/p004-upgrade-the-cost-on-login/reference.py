import base64
import hashlib
import hmac
import os

N, R, P = 2**14, 8, 1
CURRENT = (N, R, P)


# --- given: the module from the previous problem (do not change) ---------------------------
def _derive(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p, maxmem=256 * n * r)


def hash_password(password: str, *, n: int = N, r: int = R, p: int = P) -> str:
    salt = os.urandom(16)
    digest = _derive(password, salt, n, r, p)
    return "$".join(["scrypt", str(n), str(r), str(p),
                     base64.b64encode(salt).decode(), base64.b64encode(digest).decode()])


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt_b64, digest_b64 = stored.split("$")
        if scheme != "scrypt":
            return False
        expected = base64.b64decode(digest_b64)
        actual = _derive(password, base64.b64decode(salt_b64), int(n), int(r), int(p))
    except (ValueError, TypeError, AttributeError, OverflowError):
        return False
    return hmac.compare_digest(actual, expected)


# --- your part ------------------------------------------------------------------------------
def needs_rehash(stored: str, current=CURRENT) -> bool:
    """True if this hash is unreadable or weaker than `current` in n, r or p."""
    try:
        scheme, n, r, p, *_ = stored.split("$")
        if scheme != "scrypt":
            return True
        stored_cost = (int(n), int(r), int(p))
    except ValueError:
        return True
    return any(have < want for have, want in zip(stored_cost, current))


def verify_and_upgrade(password: str, stored: str, current=CURRENT):
    """Return (ok, new_hash_or_None). Call it at login: the password is in memory only now."""
    if not verify_password(password, stored):
        return False, None
    if needs_rehash(stored, current):
        n, r, p = current
        return True, hash_password(password, n=n, r=r, p=p)
    return True, None
