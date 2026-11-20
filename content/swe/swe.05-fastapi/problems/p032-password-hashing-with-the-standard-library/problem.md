# Password hashing with the standard library

Chapter section 12.1 (password hashing with the standard library). The reasons for salting and slow hashes are in swe.04 section 15.

Section 12.1 hashed with `hashlib.scrypt`. Write the same pair of functions with **`hashlib.pbkdf2_hmac`**, and store the **number of iterations inside the string**, so that you can raise it later without breaking old passwords.

**`hash_password(password, iterations=600_000) -> str`**

- a new random 16-byte salt for every call: `os.urandom(16)`;
- `digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)` (32 bytes);
- return the four parts joined with `$`:

```text
pbkdf2_sha256$<iterations>$<salt in base64>$<digest in base64>
```

(base64: `base64.b64encode(raw).decode()`; it never contains `$`.)

**`verify_password(password, stored) -> bool`**

- split `stored` into the four parts; if that fails, if the scheme is not `pbkdf2_sha256`, or if the iterations or the base64 cannot be read, return **`False`** (never raise: a broken row must not crash the login);
- recompute the digest with the **stored** salt and the **stored** iterations;
- compare with **`hmac.compare_digest(actual, expected)`**, never with `==` (a constant-time comparison; section 12.1).

## Example

```text
>>> h = hash_password("correct horse", iterations=1000)
>>> h.split("$")[:2]
['pbkdf2_sha256', '1000']
>>> verify_password("correct horse", h), verify_password("wrong", h)
(True, False)
>>> hash_password("same", iterations=1000) == hash_password("same", iterations=1000)
False                                   # a new salt each time
>>> verify_password("x", "garbage")
False
```

The default of 600,000 iterations takes about a third of a second, which is the point (it slows down an attacker who stole the database). The tests pass `iterations=1000` to stay fast. The tests import `hash_password` and `verify_password`.
