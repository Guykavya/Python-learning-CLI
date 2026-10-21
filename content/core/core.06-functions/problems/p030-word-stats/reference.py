PUNCT = ".,!?;:\"'()"


def clean_words(text):
    """Return the lowercase words of text with punctuation stripped from their ends."""
    words = []
    for piece in text.split():
        word = piece.strip(PUNCT).lower()
        if word:
            words.append(word)
    return words


def longest_word(words):
    """Return the first longest word, or '' for no words."""
    best = ""
    for w in words:
        if len(w) > len(best):
            best = w
    return best


def word_stats(text):
    """Return a dict with keys 'words', 'unique', 'longest' and 'average' for text."""
    words = clean_words(text)
    if not words:
        return {"words": 0, "unique": 0, "longest": "", "average": 0.0}
    letters = sum(len(w) for w in words)
    return {
        "words": len(words),
        "unique": len(set(words)),
        "longest": longest_word(words),
        "average": round(letters / len(words), 2),
    }
