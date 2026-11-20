def longest_repeat(s):
    """A longest substring that occurs at least twice in s (occurrences may overlap); '' if none."""
    best = ""
    for length in range(1, len(s)):
        seen = set()
        for i in range(len(s) - length + 1):
            w = s[i:i + length]                  # every substring of every length: O(n**2) windows
            if w in seen:
                best = w
                break
            seen.add(w)
    return best
