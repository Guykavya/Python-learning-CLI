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
