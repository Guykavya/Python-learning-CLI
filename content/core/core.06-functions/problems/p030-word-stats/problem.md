# Word statistics from small functions

Write `word_stats(text)` that returns a dict of statistics about the words in `text`:

| key | value |
|---|---|
| `"words"` | number of words |
| `"unique"` | number of different words |
| `"longest"` | the longest word (the first one, on a tie) |
| `"average"` | average word length, rounded to 2 decimals |

A **word** is what `split()` gives, with the punctuation characters `.,!?;:"'()` stripped from
both ends (`str.strip` with those characters) and lowercased. Pieces that become empty after
stripping (like a lone `!` or `...`) are not words.

For text with no words: `{"words": 0, "unique": 0, "longest": "", "average": 0.0}`.

**Design requirement.** Do not put everything in one function. Write at least **two helper
functions** (for example `clean_words(text)` returning the list of words, and
`longest_word(words)`), and make `word_stats` call them. The tests check that `solution.py`
defines at least three functions.

**Example**

```python
word_stats("The cat saw the other cat!")
# {'words': 6, 'unique': 4, 'longest': 'other', 'average': 3.33}
```
