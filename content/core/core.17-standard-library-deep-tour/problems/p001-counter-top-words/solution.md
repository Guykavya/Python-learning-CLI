## Approach

Split the work in two. `word_counts` does the cleaning: lower-case, split on whitespace, strip
punctuation from the ends with `str.strip(PUNCT)`, and skip empties. The counting itself is one
call: `Counter(words)`.

`top_words` then asks the counter for `most_common(n)`. It returns `(item, count)` pairs sorted by
count, high to low. The sort is **stable**: items with equal counts keep their insertion order,
and a `Counter` inserts words in the order it first meets them, so ties stay in first-seen order
for free.

The `n <= 0` guard is there to make the rule visible. `most_common(0)` and `most_common(-3)`
already return `[]` today, but `most_common(None)` returns **everything**, so be clear about what
`n` you pass.

## Code

```python
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
```

## Complexity

Counting is O(W) for W words. `most_common(n)` uses a heap when `n` is given: O(U log n) for U
different words. Memory O(U).

## Another way

You can pass a generator straight into the constructor:
`Counter(w for w in (raw.strip(PUNCT) for raw in text.lower().split()) if w)`.
Or count by hand with `counts[w] = counts.get(w, 0) + 1` and sort with
`sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:n]`. That is exactly what `Counter`
does for you, and `sorted` is also stable, so ties still keep first-seen order.
