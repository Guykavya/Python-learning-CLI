## Approach

Name the steps and give each its own function. `clean_words` turns text into a clean list; it
knows nothing about statistics. `longest_word` works on any list of words. `word_stats` just
combines them and handles the empty case first, with a guard clause, so the division is safe.
Each helper is pure and could be tested on its own.

## Code

```python
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
```

## Complexity

O(n) for a text of n characters.

## Another way

`max(words, key=len)` gives the first longest word, so `longest_word` could be one line. The point
of the exercise is the shape of the program: small pure functions with one job each, composed by
a short top-level function.
