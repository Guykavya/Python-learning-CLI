## Approach

```python
import base64
import hashlib
import hmac
import os

N, R, P = 2**14, 8, 1


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
```

Why each part is there (chapter 2.1 and 2.2):

- **Salt:** a random value per password. Two users with the same password get different strings, and an attacker cannot use one precomputed table against all of them.
- **A slow hash (scrypt):** it needs time and memory (about `128 * n * r` bytes), so every guess costs the attacker the same as it costs you.
- **Self-describing string:** the cost is written inside it, so you can raise `N` next year and old hashes still verify.
- **`hmac.compare_digest`:** constant-time comparison, so response time does not tell how many bytes matched.
- **One `except` around the parsing:** a bad string (bad base64, `n` not a number, `n` not a power of two which makes scrypt raise `ValueError`) is just "not a match".

## Complexity

Time and memory are chosen on purpose: about `O(n * r * p)` time and `128 * n * r` bytes. With the default cost, one call takes tens of milliseconds (machine-specific). The parsing is `O(length of the string)`.

## Another way

Use a library with a ready-made format: **Argon2id** (`argon2-cffi`) or **bcrypt** are the usual choices and handle salt, format and comparison for you. They are not installed in this course environment (chapter 2.2, "Try it on your machine"). `hashlib.pbkdf2_hmac` is also in the standard library but needs a very high iteration count and uses almost no memory, so it is weaker against GPUs.
