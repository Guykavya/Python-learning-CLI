def distinct_counts(a, queries):
    """For each (l, r): the number of distinct values in a[l:r]."""
    return [len(set(a[l:r])) for l, r in queries]       # O(n) per question
