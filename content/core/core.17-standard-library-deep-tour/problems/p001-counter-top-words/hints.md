## Hint 1

`Counter(iterable)` counts the items of any iterable. So if you can build a list (or a generator) of clean words, the counting is one call. What has to happen to each raw piece of `text.lower().split()` before it is counted?

## Hint 2

`str.strip(chars)` removes any of the given characters from both ends. After counting, `Counter.most_common(n)` returns `(item, count)` pairs, most common first. How does it order ties? (It is stable: first inserted comes first.) What does it do for `n = 0`?

## Hint 3

```
PUNCT = '.,!?;:"\'()'

word_counts(text):
    words = []
    for raw in text.lower().split():
        w = raw.strip(PUNCT)
        if w: words.append(w)
    return Counter(words)

top_words(text, n):
    if n <= 0: return []
    return word_counts(text).most_common(n)
```
