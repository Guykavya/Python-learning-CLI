import hashlib
import hmac
import struct


def hotp(key: bytes, counter: int, digits: int = 6) -> str:
    raise NotImplementedError("write hotp()")


def totp(key: bytes, at: float, step: int = 30, digits: int = 6) -> str:
    raise NotImplementedError("write totp()")


def verify_totp(key: bytes, code: str, now: float, last_step: int = -1):
    raise NotImplementedError("write verify_totp()")
