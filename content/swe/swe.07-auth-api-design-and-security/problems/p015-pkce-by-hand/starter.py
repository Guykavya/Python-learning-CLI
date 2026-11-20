import base64
import hashlib
import secrets


def make_verifier() -> str:
    raise NotImplementedError("write make_verifier()")


def challenge_for(verifier: str) -> str:
    raise NotImplementedError("write challenge_for()")
