## Approach

```python
import hashlib
import hmac
import struct


def hotp(key: bytes, counter: int, digits: int = 6) -> str:
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F                                       # dynamic truncation
    number = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(number % 10**digits).zfill(digits)


def totp(key: bytes, at: float, step: int = 30, digits: int = 6) -> str:
    return hotp(key, int(at) // step, digits)


def verify_totp(key: bytes, code: str, now: float, last_step: int = -1):
    if not isinstance(code, str) or len(code) != 6 or not (code.isascii() and code.isdigit()):
        return None
    current = int(now) // 30
    for s in range(current - 1, current + 2):
        if s > last_step and hmac.compare_digest(hotp(key, s), code):
            return s
    return None
```

The vectors of both RFCs pass with this code (checked by running it). The replay rule is the single condition `s > last_step`: a slot that was used, or any older one, can never be accepted again, so an observed code is worth nothing after the real user has used it. The caller stores the returned slot (in the user's database row) and passes it back next time. The code is checked as text so that `047291` keeps its zero. The ASCII guard is needed because `str.isdigit()` is also true for digits of other scripts, and `compare_digest` raises `TypeError` for non-ASCII text.

## Complexity

At most three HMAC computations per check: O(1).

## Another way

Compute the three candidate codes first, then compare each with `compare_digest` without returning early, so the time is identical whether the first or the last slot matches. Either way, rate-limit attempts: a 6-digit code has only a million values (chapter 6.3).

## Not covered

Recovery codes and the QR-code secret in base32 are described in the chapter.
