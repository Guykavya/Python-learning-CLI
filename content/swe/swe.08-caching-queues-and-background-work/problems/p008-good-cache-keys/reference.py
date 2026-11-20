import hashlib

MAX_PARAMS_LENGTH = 64


def cache_key(namespace, version, **params):
    if not isinstance(namespace, str) or not namespace or ":" in namespace or any(c.isspace() for c in namespace):
        raise ValueError(f"bad namespace {namespace!r}: non-empty, no ':' and no whitespace")
    kept = sorted((name, value) for name, value in params.items() if value is not None)
    if not kept:
        return f"{namespace}:v{version}"
    part = "&".join(f"{name}={value}" for name, value in kept)
    if len(part) > MAX_PARAMS_LENGTH or any(c.isspace() for c in part):
        part = "sha256=" + hashlib.sha256(part.encode("utf-8")).hexdigest()
    return f"{namespace}:v{version}:{part}"
