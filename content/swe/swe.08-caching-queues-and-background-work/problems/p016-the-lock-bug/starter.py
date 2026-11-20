import secrets


def new_token():
    return "token"                    # TODO: a random token per acquire


def acquire(r, name, token, ttl=10):
    return bool(r.set(f"lock:{name}", token, ex=ttl, nx=True))


def release(r, name, token):
    r.delete(f"lock:{name}")          # BUG: deletes whoever holds the lock now
    return True
