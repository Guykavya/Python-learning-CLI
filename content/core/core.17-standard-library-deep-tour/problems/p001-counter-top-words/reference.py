from collections import Counter

PUNCT = ".,!?;:\"'()"


def word_counts(text: str) -> Counter[str]:
    words = []
    for raw in text.lower().split():
        word = raw.strip(PUNCT)
        if word:
            words.append(word)
    return Counter(words)


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    if n <= 0:
        return []
    return word_counts(text).most_common(n)
