def count_vowels(text):
    """Return how many vowels (a, e, i, o, u, any case) are in text."""
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count
