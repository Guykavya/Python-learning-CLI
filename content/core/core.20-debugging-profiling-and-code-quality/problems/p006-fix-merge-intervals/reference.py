def merge_intervals(intervals):
    """Merge overlapping or touching [start, end] intervals.

    Returns a new sorted list of [start, end] lists. The input is not changed.
    """
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])  # a NEW list, never the caller's
    return merged
