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
