PUNCTUATION = ".,!?;:\"'()[]{}-_"


def word_frequency(text):
    """Return a dict mapping each word to its number of occurrences."""
    counts = {}
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word == "":
            continue
        counts[word] = counts.get(word, 0) + 1
    return counts
