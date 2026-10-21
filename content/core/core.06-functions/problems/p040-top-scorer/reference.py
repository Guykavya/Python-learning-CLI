def top_scorer(scores):
    """Return the name with the highest score (alphabetically first on a tie), or None if empty."""
    return min(scores, key=lambda name: (-scores[name], name), default=None)
