def prefix_function(s):
    """pi[i] = length of the longest proper prefix of s[:i+1] that is also its suffix."""
    pi = []
    for i in range(len(s)):
        t = s[:i + 1]
        best = 0
        for k in range(1, len(t)):            # straight from the definition: O(n**3) in the worst case
            if t[:k] == t[-k:]:
                best = k
        pi.append(best)
    return pi
