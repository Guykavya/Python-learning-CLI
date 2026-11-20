def allow(r, user, limit, window, now):
    """True if this request is within the limit. BUGGY: fix it."""
    key = f"rate:{user}:{int(now() // window)}"
    count = int(r.get(key) or 0)
    if count >= limit:
        return False
    r.set(key, count + 1, ex=window)
    return True
