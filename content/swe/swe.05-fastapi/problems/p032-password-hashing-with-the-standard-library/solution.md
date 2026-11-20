## Approach

```python
SCHEME = "pbkdf2_sha256"


def hash_password(password: str, iterations: int = 600_000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    parts = [SCHEME, str(iterations), base64.b64encode(salt).decode(), base64.b64encode(digest).decode()]
    return "$".join(parts)


def verify_password(password: str, stored: str) -> bool:
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
```

Each part of the string has a job:

- **scheme**: lets you switch algorithms later. A new login can check `scheme` and re-hash with the new one.
- **iterations**: the cost. Today 600,000; in three years perhaps 1,200,000. Old hashes keep their own count and still verify; when a user logs in successfully you can re-hash with the new count.
- **salt**: random per password, so two users with the same password get different hashes, and an attacker cannot use one precomputed table for everyone.
- **digest**: the result.

`hmac.compare_digest` takes the same time whether the first byte differs or the last, so response timing reveals nothing about how close a guess was.

## Complexity

O(iterations) per hash and per verify. That cost is deliberate: an attacker who stole the table pays it for every guess.

## Another way

Keep `hashlib.scrypt` (section 12.1), which is "memory-hard" and so more expensive to attack with special hardware; store `n`, `r`, `p` in the string the same way. In production, libraries like `argon2-cffi` or `bcrypt` produce this kind of self-describing string for you.
