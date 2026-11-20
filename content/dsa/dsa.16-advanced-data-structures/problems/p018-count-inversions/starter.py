def count_inversions(a):
    """Number of pairs i < j with a[i] > a[j]."""
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])     # O(n**2)
