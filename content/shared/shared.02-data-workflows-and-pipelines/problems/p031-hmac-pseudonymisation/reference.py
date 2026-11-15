import hashlib
import hmac
import os

ENV_VAR = "PAGEBOUND_PSEUDO_KEY"
MIN_LENGTH = 16


def load_secret(env=None):
    if env is None:
        env = os.environ
    value = env.get(ENV_VAR, "").strip()
    if not value:
        raise RuntimeError(f"{ENV_VAR} is not set; export it before running the pipeline")
    if len(value) < MIN_LENGTH:
        raise RuntimeError(f"{ENV_VAR} is too short; use at least {MIN_LENGTH} characters")
    return value.encode("utf-8")


def pseudonymise(value, key):
    if value is None:
        return None
    normalised = value.strip().lower()
    return hmac.new(key, normalised.encode("utf-8"), hashlib.sha256).hexdigest()[:16]


def pseudonymise_rows(rows, key, field="email", out_field="customer_key"):
    out = []
    for row in rows:
        new = {}
        for name, value in row.items():
            if name == field:
                new[out_field] = pseudonymise(value, key)
            else:
                new[name] = value
        if field not in row:
            new[out_field] = None
        out.append(new)
    return out
