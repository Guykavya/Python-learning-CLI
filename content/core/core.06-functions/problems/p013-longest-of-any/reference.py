def longest(*words):
    """Return the longest word given (the first one on a tie), or "" if none are given."""
    best = ""
    for w in words:
        if len(w) > len(best):
            best = w
    return best
