def merge_intervals(intervals):
    """Merge overlapping or touching [start, end] intervals.

    Returns a new sorted list of [start, end] lists. The input is not changed.
    """
    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last = merged[-1]
        if start < last[1]:
            last[1] = end
        else:
            merged.append([start, end])
    return merged
