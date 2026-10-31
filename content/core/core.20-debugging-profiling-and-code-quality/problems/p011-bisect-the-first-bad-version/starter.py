def first_bad(versions: list, is_bad):
    """First version for which is_bad is True (versions are good, then bad), or None."""
    for v in versions:  # correct, but tests EVERY version: far too many calls
        if is_bad(v):
            return v
    return None
