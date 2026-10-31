## Approach

- **Token**: `token_urlsafe(32)` takes 32 bytes from the OS random source and encodes them in
  URL-safe base64 (letters, digits, `-`, `_`), which gives 43 characters. 32 bytes is 256 bits:
  nobody will ever guess it.
- **Password**: random characters from the full alphabet often miss a kind (with 8 characters,
  "no symbol" happens about 30% of the time), so guarantee one of each kind first, fill the rest
  from the full alphabet, then shuffle with `secrets.SystemRandom()`, a `random.Random`-like
  object whose numbers come from the OS source, so the guaranteed characters can be anywhere.
- **Comparison**: `==` stops at the first different character, so a wrong guess with a correct
  start takes slightly longer. Measured many times, that difference leaks the secret one character
  at a time. `compare_digest` takes the same time wherever the difference is. It accepts `str` only
  when it is ASCII, so encode to UTF-8 bytes first.

## Code

```python
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
```

## Complexity

O(length) for the password, O(nbytes) for the token and O(n) for the comparison (it always looks
at every byte, by design).

## Another way

The Python documentation shows a "retry" recipe: generate `"".join(secrets.choice(ALPHABET) for _ in range(length))`
in a loop until it contains every kind. It is simple and gives a perfectly uniform result among
valid passwords; on average it needs only a few tries for 16 characters. `hmac.compare_digest` is
the same function as `secrets.compare_digest`.
