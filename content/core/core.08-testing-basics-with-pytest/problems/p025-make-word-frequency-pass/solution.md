## Approach

Three small steps for every raw piece: lower-case it, strip the punctuation from the ends only, skip it if nothing is left. Counting uses `dict.get(word, 0) + 1`. `str.split()` with no argument already treats any run of whitespace as one separator, which also makes blank text give an empty dict.

## Code

```python
PUNCTUATION = ".,!?;:\"'()[]{}-_"


def word_frequency(text):
    counts = {}
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word == "":
            continue
        counts[word] = counts.get(word, 0) + 1
    return counts
```

## Complexity

O(n) for n characters, one pass.

## Another way

Strip from each end with a loop checking `isalnum()`. That works for every symbol, not only the ones in your list. The apostrophe in `"don't"` stays because it is in the middle.

The apostrophe is in `PUNCTUATION` as well, so a quoted word like `'hello'` loses its quotes while `don't` keeps its inner one.
