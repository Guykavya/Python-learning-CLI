import hashlib
import hmac
import os

ENV_VAR = "PAGEBOUND_PSEUDO_KEY"


def load_secret(env=None):
    """Read the key from env (default os.environ) and return it as bytes; RuntimeError if unusable."""
    raise NotImplementedError("read ENV_VAR, check it, encode it")


def pseudonymise(value, key):
    """Stable, keyed, one-way: hmac-sha256 of the normalised value, first 16 hex characters."""
    raise NotImplementedError("hmac.new(key, message_bytes, hashlib.sha256).hexdigest()[:16]")


def pseudonymise_rows(rows, key, field="email", out_field="customer_key"):
    """New rows where `field` is replaced by `out_field` holding the pseudonym."""
    raise NotImplementedError("build new dicts; never keep the original email")
