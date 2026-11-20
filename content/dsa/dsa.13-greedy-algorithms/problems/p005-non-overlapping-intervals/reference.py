def min_removals(intervals):
    """Fewest intervals to delete so that the rest do not overlap (touching is fine)."""
    kept = 0
    last_end = float("-inf")
    for s, e in sorted(intervals, key=lambda iv: iv[1]):
        if s >= last_end:              # keep it: it fits after the last kept interval
            kept += 1
            last_end = e
    return len(intervals) - kept
