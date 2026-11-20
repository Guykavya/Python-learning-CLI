## Approach

```python
import base64
import hashlib
import re
import secrets

_ALLOWED = re.compile(r"[A-Za-z0-9\-._~]{43,128}")


def make_verifier() -> str:
    return secrets.token_urlsafe(48)           # 64 characters from A-Z a-z 0-9 - _


def challenge_for(verifier: str) -> str:
    if not _ALLOWED.fullmatch(verifier):
        raise ValueError("a code verifier is 43 to 128 characters from A-Z a-z 0-9 - . _ ~")
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
```

48 random bytes become 64 base64url characters, inside the 43 to 128 range. The challenge is a one-way hash: from the challenge nobody can compute the verifier, so a thief who sees `code_challenge` in the redirect URL learns nothing useful. Use `fullmatch`, not `match`: `match` would accept a valid prefix followed by junk.

## Complexity

O(length of the verifier). One SHA-256 call.

## Another way

Build the verifier yourself: `"".join(secrets.choice(ALPHABET) for _ in range(64))` with the full 66-character alphabet. It is slower and gains nothing, but shows that any random string from the allowed set will do. The `plain` method (challenge equals verifier) exists in the RFC but must not be used: it protects nothing.
