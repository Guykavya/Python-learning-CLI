def max_activities(intervals):
    """Largest number of non-overlapping (start, end) requests; touching is allowed."""
    count = 0
    last_end = float("-inf")
    for s, e in sorted(intervals, key=lambda iv: (iv[1], iv[0])):
        if s >= last_end:              # fits after the last chosen event (touching is fine)
            count += 1
            last_end = e
    return count
