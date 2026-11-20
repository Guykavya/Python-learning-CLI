def allow(r, user, limit, window, now):
    """True if this request is within the limit (fixed window, shared by every worker)."""
    key = f"rate:{user}:{int(now() // window)}"
    r.set(key, 0, ex=window, nx=True)        # create-with-expiry in ONE atomic command (no-op if it exists)
    return r.incr(key) <= limit               # INCR is atomic and keeps the TTL
