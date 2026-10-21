def word_frequency(text):
    """Return a dict mapping each word to its number of occurrences."""
    counts = {}
    for word in text.split(" "):
        counts[word] = counts.get(word, 0) + 1
    return counts
