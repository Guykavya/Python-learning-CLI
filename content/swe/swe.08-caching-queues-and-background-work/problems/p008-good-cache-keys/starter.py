import hashlib


def cache_key(namespace, version, **params):
    # TODO: validate the namespace, drop None, sort, join, hash if long or spaced
    return f"{namespace}:{params}"
