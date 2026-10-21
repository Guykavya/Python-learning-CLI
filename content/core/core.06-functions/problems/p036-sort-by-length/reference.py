def sort_by_length(words):
    """Return words sorted by length, then alphabetically ignoring case."""
    return sorted(words, key=lambda w: (len(w), w.lower()))
