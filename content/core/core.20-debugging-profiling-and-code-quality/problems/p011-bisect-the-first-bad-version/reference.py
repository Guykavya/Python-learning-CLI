def first_bad(versions: list, is_bad):
    """First version for which is_bad is True (versions are good, then bad), or None."""
    lo, hi = 0, len(versions)  # the answer's index is in [lo, hi]; hi == len means "none"
    while lo < hi:
        mid = (lo + hi) // 2
        if is_bad(versions[mid]):
            hi = mid
        else:
            lo = mid + 1
    return versions[lo] if lo < len(versions) else None
