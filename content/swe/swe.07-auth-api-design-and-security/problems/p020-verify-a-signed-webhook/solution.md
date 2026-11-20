## Approach

```python
import hashlib
import hmac

TOLERANCE = 300


def receive(body: bytes, ts: int, signature: str, now: int, secret: bytes) -> str:
    if abs(now - ts) > TOLERANCE:
        return "stale"
    expected = hmac.new(secret, f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    try:
        given = signature.encode("ascii")
    except (UnicodeEncodeError, AttributeError):
        return "bad signature"
    if not hmac.compare_digest(expected.encode("ascii"), given):
        return "bad signature"
    return "ok"
```

The cheap check (time) comes first: stale requests are dropped without any hashing. The timestamp is part of the signed text, so an attacker cannot take an old valid body and attach a fresh timestamp. Comparing as bytes avoids the `TypeError` that `compare_digest` raises for non-ASCII `str`. The body is hashed exactly as it arrived, which is why a re-serialised copy of the same JSON fails.

## Complexity

One HMAC over the body: O(len(body)).

## Another way

Providers often send several signatures in one header (to rotate secrets) as `t=...,v1=...`. The receiver then accepts if any `v1` matches. You can build that on top: parse the header, loop over the candidates, and use the same comparison. For duplicate deliveries, store the event id (chapter 6.4) after the signature check passes.
