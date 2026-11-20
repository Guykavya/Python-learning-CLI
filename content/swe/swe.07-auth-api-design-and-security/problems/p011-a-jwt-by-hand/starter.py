import base64
import hashlib
import hmac
import json


class InvalidToken(Exception):
    """The token is malformed, forged, or not signed the way we expect."""


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64u_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def sign(payload: dict, key: bytes) -> str:
    # TODO: header.payload.signature, as described in problem.md
    return ""


def verify(token: str, key: bytes) -> dict:
    # TODO: three parts, signature first (compare_digest), then alg, then the payload
    raise NotImplementedError
