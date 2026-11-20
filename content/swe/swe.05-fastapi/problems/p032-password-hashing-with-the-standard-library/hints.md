## Hint 1

What does `verify_password` need to recompute the digest? The password (given), the **salt** and the **iterations** that were used when the hash was made. Both must therefore be inside the stored string. Section 12.1's `scrypt` version stores the salt; you add the iterations as one more `$` part.

## Hint 2

Parsing can fail in several ways: wrong number of parts (`a, b, c, d = s.split("$")` raises `ValueError`), iterations not a number (`int("many")` raises `ValueError`), bad base64 (`base64.b64decode(text, validate=True)` raises `binascii.Error`, which is a subclass of `ValueError`). One `try ... except ValueError: return False` covers them all.

## Hint 3

```text
hash_password(password, iterations=600_000):
    salt = os.urandom(16)
    digest = pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return "$".join(["pbkdf2_sha256", str(iterations), b64(salt), b64(digest)])

verify_password(password, stored):
    try: scheme, n, salt_b64, digest_b64 = stored.split("$"); n = int(n); salt, expected = b64decode(...) (validate=True)
    except ValueError: return False
    if scheme != "pbkdf2_sha256" or n < 1: return False
    return hmac.compare_digest(pbkdf2_hmac("sha256", password.encode(), salt, n), expected)
```
