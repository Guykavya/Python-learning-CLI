import base64
import hashlib
import hmac
import os

N, R, P = 2**14, 8, 1            # the current cost: 16 MiB of memory (machine-specific time)


def hash_password(password: str, *, n: int = N, r: int = R, p: int = P) -> str:
    # TODO: random 16-byte salt, scrypt digest, "scrypt$n$r$p$salt_b64$digest_b64"
    return ""


def verify_password(password: str, stored: str) -> bool:
    # TODO: split the string, recompute with ITS parameters, compare with hmac.compare_digest
    return False
