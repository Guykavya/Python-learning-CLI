# Counter: the most common words

Counting things is so common that the standard library has a dict made for it:
`collections.Counter`. It counts any iterable in one line and can give you the most common
items, already sorted.

Write two functions in `solution.py`.

1. `word_counts(text: str) -> Counter[str]`
   - Lower-case the text and split it on whitespace.
   - Strip these punctuation marks from **both ends** of every word: `.,!?;:"'()`
   - Skip anything that becomes empty after stripping (for example a lone `-` is kept, but a lone `!` is skipped).
   - Return a `Counter` (not a plain dict).
2. `top_words(text: str, n: int) -> list[tuple[str, int]]`
   - The `n` most common words with their counts, most common first.
   - Words with the **same count** stay in the order they **first appeared** in the text.
   - `n` larger than the number of different words gives all of them; `n <= 0` gives `[]`.

**Example**

```python
word_counts("The cat. The dog!")
# Counter({'the': 2, 'cat': 1, 'dog': 1})

top_words("b a b c a b", 2)
# [('b', 3), ('a', 2)]

top_words("one two three", 2)
# [('one', 1), ('two', 1)]      ties keep first-seen order
```
