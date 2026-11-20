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
