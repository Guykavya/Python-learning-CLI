## Hint 1

Which steps can you name? Turning text into clean words is one job; finding the longest is another.

## Hint 2

```
def clean_words(text):
    words = []
    for piece in text.split():
        w = piece.strip(PUNCT).lower()
        if w: words.append(w)
    return words
```

## Hint 3

```
def word_stats(text):
    words = clean_words(text)
    if not words: return the empty-stats dict
    total_letters = sum(len(w) for w in words)
    return {"words": len(words), "unique": len(set(words)),
            "longest": longest_word(words), "average": round(total_letters / len(words), 2)}
```
