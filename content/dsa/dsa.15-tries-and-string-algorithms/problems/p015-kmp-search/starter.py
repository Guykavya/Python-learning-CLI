def kmp_search(text, pattern):
    """All start positions of pattern in text, overlapping ones included."""
    found, start = [], 0
    while True:
        i = text.find(pattern, start)
        if i == -1:
            return found
        found.append(i)
        start = i + len(pattern)          # skips overlapping matches
