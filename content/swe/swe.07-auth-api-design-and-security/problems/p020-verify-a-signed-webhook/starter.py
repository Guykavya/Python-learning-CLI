import hashlib
import hmac

TOLERANCE = 300


def receive(body: bytes, ts: int, signature: str, now: int, secret: bytes) -> str:
    raise NotImplementedError("write receive()")
