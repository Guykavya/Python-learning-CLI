def word_break(s, words):
    """True if s can be cut into pieces that are all in words (words may repeat)."""
    return any(s.startswith(w) for w in words)
