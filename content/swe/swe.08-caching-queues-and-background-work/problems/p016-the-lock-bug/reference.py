import secrets


def new_token():
    return secrets.token_hex(16)


def acquire(r, name, token, ttl=10):
    return bool(r.set(f"lock:{name}", token, ex=ttl, nx=True))


def release(r, name, token):
    # compare-and-delete in ONE atomic command (a Lua script in real Redis)
    return r.delete_if_equals(f"lock:{name}", token) == 1
