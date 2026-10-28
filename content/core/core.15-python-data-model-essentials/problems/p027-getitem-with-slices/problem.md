# __getitem__ that understands slices

For `x[2:5]` Python calls `x.__getitem__(slice(2, 5, None))`. So one method receives an `int` for
`x[2]` and a `slice` object for `x[2:5]`. A well-behaved sequence returns **its own type** when sliced.

Write `Sentence(words)` in `solution.py`:

- `Sentence(words)` takes an iterable of words and keeps them in a list.
- `len(s)` is the word count.
- `s[i]` is a word (negative indexes work; bad indexes raise `IndexError`).
- `s[a:b]` (and `s[::2]`, `s[::-1]`...) returns a **new `Sentence`** (not a list) with the selected words.
- Any other index type (like a string) raises `TypeError`.
- `repr(s)` is `Sentence(['the', 'quick', 'fox'])`; `str(s)` is the words joined with single spaces.

**Example**

```python
s = Sentence(["the", "quick", "brown", "fox"])
print(s[1])        # quick
print(s[1:3])      # Sentence(['quick', 'brown'])
print(s[::-1])     # Sentence(['fox', 'brown', 'quick', 'the'])
print(str(s[:2]))  # the quick
s["a"]             # TypeError
```
