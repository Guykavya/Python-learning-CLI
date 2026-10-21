def tally(votes):
    """Return a dict from cleaned candidate name to number of votes."""
    counts = {}
    for vote in votes:
        name = vote.strip().lower()
        if not name:
            continue
        try:
            counts[name] += 1
        except KeyError:
            counts[name] = 1
    return counts
