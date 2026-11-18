def insert_interval(intervals, new):
    """Insert `new` into a sorted list of disjoint blocks; touching blocks merge."""
    ns, ne = new
    out = []
    i = 0
    n = len(intervals)
    while i < n and intervals[i][1] < ns:          # 1) ends before new starts: copy
        out.append([intervals[i][0], intervals[i][1]])
        i += 1
    while i < n and intervals[i][0] <= ne:         # 2) overlaps or touches new: absorb
        ns = min(ns, intervals[i][0])
        ne = max(ne, intervals[i][1])
        i += 1
    out.append([ns, ne])
    while i < n:                                   # 3) starts after new ends: copy
        out.append([intervals[i][0], intervals[i][1]])
        i += 1
    return out
