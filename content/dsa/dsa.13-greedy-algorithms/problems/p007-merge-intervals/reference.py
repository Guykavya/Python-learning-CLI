def merge(intervals):
    """Merge overlapping or touching (start, end) intervals; return sorted [start, end] lists."""
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:             # overlaps or touches the current block
            out[-1][1] = max(out[-1][1], e)     # extend; max matters
        else:
            out.append([s, e])
    return out
