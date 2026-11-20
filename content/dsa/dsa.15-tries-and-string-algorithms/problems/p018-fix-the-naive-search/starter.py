def find_all(text, pattern):
    """All start positions of pattern in text, overlapping ones included. pattern is not empty."""
    n, m = len(text), len(pattern)
    found = []
    for start in range(n - m + 1):
        k = 0
        while k < m and text[start + k] == pattern[k]:
            k += 1
        if k == m:
            found.append(start)
    return found
