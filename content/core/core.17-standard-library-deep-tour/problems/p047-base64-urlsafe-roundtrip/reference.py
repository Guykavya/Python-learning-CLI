import base64
import string

ALPHABET = set(string.ascii_letters + string.digits + "-_")


def encode_token(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def decode_token(token):
    body = token.rstrip("=")
    for ch in body:
        if ch not in ALPHABET:
            raise ValueError(f"invalid character {ch!r} in token")
    padded = body + "=" * (-len(body) % 4)
    return base64.urlsafe_b64decode(padded)     # binascii.Error is a ValueError


def encode_text(text):
    return encode_token(text.encode("utf-8"))


def decode_text(token):
    return decode_token(token).decode("utf-8")
