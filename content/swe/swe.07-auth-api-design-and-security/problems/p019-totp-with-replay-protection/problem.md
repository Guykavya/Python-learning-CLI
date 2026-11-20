# TOTP with replay protection

Chapter section 6.3 (one-time codes: TOTP) and "Try it: the TOTP replay". An authenticator app and the server share a secret key. Both compute a short code from the key and the current 30-second **slot**. The algorithm is in two RFCs, and both publish test values.

Write three functions in `solution.py`:

- `hotp(key: bytes, counter: int, digits: int = 6) -> str` (RFC 4226): `mac = HMAC-SHA1(key, counter as 8 bytes, big-endian)`. Take `offset = mac[-1] & 0x0F`, read 4 bytes at `offset` as a big-endian unsigned number, clear its top bit (`& 0x7FFFFFFF`), take it modulo `10**digits` and **pad with leading zeros** to `digits` characters.
- `totp(key: bytes, at: float, step: int = 30, digits: int = 6) -> str` (RFC 6238): `hotp(key, int(at) // step, digits)`.
- `verify_totp(key: bytes, code: str, now: float, last_step: int = -1)`: accept a 6-digit `code` if it is the code of the slot `current - 1`, `current` or `current + 1` (clock drift), where `current = int(now) // 30` **and** that slot is greater than `last_step`. Return the slot number that matched, so the caller can store it as the new `last_step`; return `None` otherwise. Compare with `hmac.compare_digest`. A `code` that is not exactly 6 ASCII digits gives `None`; the function never raises.

Nothing is read from a clock: `now` is an argument.

## Example

```python
KEY = b"12345678901234567890"             # the RFC test secret
totp(KEY, 59, digits=8)                   # '94287082'  (RFC 6238 appendix B)
hotp(KEY, 0)                              # '755224'    (RFC 4226 appendix D)

now = 1_700_000_010
code = totp(KEY, now)
slot = verify_totp(KEY, code, now)        # 56666667: first use works
verify_totp(KEY, code, now + 5, slot)     # None: the same slot is used up
```

## Why the memory matters

An attacker who looks over a shoulder and types the same code within 30 seconds sends a code that is still correct. Only the server's memory of the last used slot rejects it.
