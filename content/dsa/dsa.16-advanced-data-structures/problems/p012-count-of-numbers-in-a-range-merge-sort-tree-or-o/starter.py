def count_below(a, queries):
    """For each (l, r, x): how many of a[l:r] are strictly less than x."""
    return [sum(1 for v in a[l:r] if v < x) for l, r, x in queries]     # O(n) per question
