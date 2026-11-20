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


def _json_part(data: dict) -> str:
    return b64u(json.dumps(data, separators=(",", ":")).encode("utf-8"))


def _signature(signing_input: str, key: bytes) -> str:
    return b64u(hmac.new(key, signing_input.encode("ascii"), hashlib.sha256).digest())


def sign(payload: dict, key: bytes) -> str:
    signing_input = _json_part({"alg": "HS256", "typ": "JWT"}) + "." + _json_part(payload)
    return signing_input + "." + _signature(signing_input, key)


def verify(token: str, key: bytes) -> dict:
    try:
        head, body, sig = token.split(".")
        expected = _signature(head + "." + body, key)
        if not hmac.compare_digest(expected.encode("ascii"), sig.encode("ascii")):
            raise InvalidToken("bad signature")
        header = json.loads(b64u_decode(head))
        payload = json.loads(b64u_decode(body))
    except InvalidToken:
        raise
    except (ValueError, TypeError, AttributeError) as exc:      # split, ascii, base64 and JSON errors are all ValueError
        raise InvalidToken("malformed token") from exc
    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise InvalidToken("algorithm not allowed")
    if not isinstance(payload, dict):
        raise InvalidToken("payload is not an object")
    return payload
